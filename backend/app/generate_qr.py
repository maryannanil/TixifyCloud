import qrcode
import os
import sqlite3

# Set directory to store QR codes
QR_DIR = os.path.join(os.getcwd(), "../data/qrcodes")
os.makedirs(QR_DIR, exist_ok=True)  # Ensure directory exists

# Path to database
DB_PATH = os.path.join(os.getcwd(), "../app/tickets.db")

def generate_qr(ticket_id):
    """Generate QR code for a ticket and save it as an image."""
    qr = qrcode.make(ticket_id)
    qr_path = os.path.join(QR_DIR, f"{ticket_id}.png")
    qr.save(qr_path)
    return qr_path

def update_ticket_qr(ticket_id):
    """Generate a QR code and store its path in the database."""
    qr_path = generate_qr(ticket_id)
    
    try:
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("UPDATE tickets SET qr_code = ? WHERE ticket_id = ?", (qr_path, ticket_id))
        conn.commit()
        conn.close()
        print(f"✅ QR Code generated and saved for {ticket_id}: {qr_path}")
    except sqlite3.Error as e:
        print(f"🚨 Database error: {e}")

# Generate QR for all existing tickets
if __name__ == "__main__":
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT ticket_id FROM tickets")
    tickets = cursor.fetchall()
    conn.close()

    for ticket in tickets:
        update_ticket_qr(ticket[0])  # Generate and store QR code for each ticket
