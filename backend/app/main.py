from fastapi import FastAPI, UploadFile, Form, File, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
import sqlite3
from PIL import Image
from pyzbar.pyzbar import decode
import qrcode
import os

app = FastAPI()

DB_PATH = os.path.join(os.getcwd(), "tickets.db")
QR_DIR = os.path.join(os.getcwd(), "data/qrcodes")
os.makedirs(QR_DIR, exist_ok=True)  # Ensure QR directory exists

print("🔥 API is using database:", DB_PATH)

# -------------------- CORS Middleware --------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# -------------------- Database Setup --------------------
def ensure_db():
    """Ensure the tickets table exists before running queries."""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            event_name TEXT,
            venue TEXT,
            date TEXT,
            qr_code TEXT,
            status TEXT,
            time TEXT
        );
    """)
    conn.commit()
    conn.close()

ensure_db()

# -------------------- DB Functions --------------------
def check_ticket_in_db(ticket_id: str):
    """Check if ticket exists and is valid."""
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT status FROM tickets WHERE LOWER(ticket_id) = ?", (ticket_id.lower(),))
        result = cursor.fetchone()
        conn.close()
        return result
    except sqlite3.Error as e:
        print("🚨 Database error:", e)
        return None

# -------------------- QR Code Generation --------------------
def generate_qr(ticket_id):
    """Generate and save a QR code for a ticket."""
    qr = qrcode.make(ticket_id)
    qr_path = os.path.join(QR_DIR, f"{ticket_id}.png")
    qr.save(qr_path)
    return qr_path

def update_ticket_qr(ticket_id):
    """Generate a QR code and update database."""
    qr_path = generate_qr(ticket_id)
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE tickets SET qr_code = ? WHERE ticket_id = ?", (qr_path, ticket_id))
        conn.commit()
        conn.close()
        print(f"✅ QR Code generated and saved for {ticket_id}: {qr_path}")
    except sqlite3.Error as e:
        print("🚨 Database error:", e)

# Generate QR for all existing tickets
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()
cursor.execute("SELECT ticket_id FROM tickets")
tickets = cursor.fetchall()
conn.close()
for ticket in tickets:
    update_ticket_qr(ticket[0])

# -------------------- QR Code Retrieval --------------------
@app.get("/get_qr/{ticket_id}")
async def get_qr(ticket_id: str):
    """Retrieve and return the QR code image for a ticket."""
    qr_path = os.path.join(QR_DIR, f"{ticket_id}.png")
    if os.path.exists(qr_path):
        return FileResponse(qr_path, media_type="image/png")
    else:
        raise HTTPException(status_code=404, detail="QR code not found")

# -------------------- QR Code/Barcode Reader --------------------
def scan_ticket_from_image(image_path: str):
    """Extract QR/Barcode ticket ID from image."""
    try:
        image = Image.open(image_path)
        decoded_objects = decode(image)
        for obj in decoded_objects:
            return obj.data.decode('utf-8')  # Return first decoded QR/barcode data
        return None
    except Exception as e:
        print("🚨 Error reading QR:", e)
        return None

# -------------------- Ticket Validation API --------------------
@app.post("/validate_ticket")
async def validate_ticket(
    ticket_id: str = Form(None),  # Optional form input
    file: UploadFile = File(None)  # Optional file upload
):
    if not ticket_id and not file:
        raise HTTPException(status_code=400, detail="Please provide a Ticket ID or upload a file.")

    # ---------------- Direct Ticket ID Input ----------------
    if ticket_id:
        result = check_ticket_in_db(ticket_id.strip())
        if result and result[0] == "valid":
            return JSONResponse(content={"message": "Valid Ticket"})
        else:
            return JSONResponse(content={"message": "Invalid Ticket"})

    # ---------------- File Upload & QR/Barcode Scan ----------------
    if file:
        os.makedirs("uploads", exist_ok=True)
        file_path = os.path.join("uploads", file.filename)
        await file.seek(0)
        with open(file_path, "wb") as buffer:
            buffer.write(await file.read())

        extracted_ticket_id = scan_ticket_from_image(file_path)

        if extracted_ticket_id:
            result = check_ticket_in_db(extracted_ticket_id.strip())
            if result and result[0] == "valid":
                return JSONResponse(content={"message": f" Valid Ticket ({extracted_ticket_id})"})
            else:
                return JSONResponse(content={"message": " Invalid Ticket"})
        else:
            return JSONResponse(content={"message": " No valid QR/Barcode found in image"})
