import sqlite3
import os

db_path = os.path.join(os.getcwd(), "tickets.db")

print("Using database path:", os.path.join(os.getcwd(), "tickets.db"))

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

tickets_to_add = [
    ("mjk-333-xyz", "Shawn Mendes Tour", "Goa Beach", "2025-09-10", "qr-mjk-333-xyz", "valid", "19:30"),
    ("prs-555-stu", "Post Malone Live", "Kolkata Arena", "2025-11-25", "qr-prs-555-stu", "valid", "21:00"),
]

# Force insert & ignore duplicates
cursor.executemany("INSERT OR IGNORE INTO tickets VALUES (?, ?, ?, ?, ?, ?, ?);", tickets_to_add)

conn.commit()
print("Tickets inserted successfully!")

# Verify data
cursor.execute("SELECT * FROM tickets;")
print("Updated Tickets in DB:", cursor.fetchall())

conn.close()
