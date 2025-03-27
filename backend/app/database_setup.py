# database_setup.py

import sqlite3

def create_and_insert_valid_tickets():
    # Connect to (or create) the tickets.db
    conn = sqlite3.connect('tickets.db')
    cursor = conn.cursor()

    # Create the tickets table
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_id TEXT PRIMARY KEY,
            concert_name TEXT,
            venue TEXT,
            date TEXT,
            time TEXT,
            qr_code TEXT,
            status TEXT DEFAULT 'valid'
        )
    ''')

    # Valid tickets only
    valid_tickets = [
        ('abc-123-xyz', 'Zayn Malik Live', 'Delhi Stadium', '2025-06-20', '19:00', 'qr-abc-123-xyz', 'valid'),
        ('cas-111-aaa', 'CAS DJ Night', 'Mumbai Arena', '2025-07-10', '21:00', 'qr-cas-111-aaa', 'valid'),
        ('zae-222-bbb', 'Zaeden Concert', 'Pune Grounds', '2025-08-05', '20:00', 'qr-zae-222-bbb', 'valid'),
        ('ati-333-ccc', 'Atif Aslam Live', 'Bangalore Stadium', '2025-09-15', '19:30', 'qr-ati-333-ccc', 'valid'),
        ('wkd-721-bli', 'The Weekend', 'DY Patil Stadium', '2025-12-15', '19:30', 'qr-wkd-721-bli', 'valid')
    ]

    # Insert tickets (skip if exists)
    cursor.executemany('''
        INSERT OR IGNORE INTO tickets (ticket_id, concert_name, venue, date, time, qr_code, status)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', valid_tickets)

    # Save and close
    conn.commit()
    conn.close()

    print(" Tickets table created and valid tickets inserted successfully!")

if __name__ == '__main__':
    create_and_insert_valid_tickets()