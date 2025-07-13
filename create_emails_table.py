import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

# Drop the old emails table if it exists
cursor.execute("DROP TABLE IF EXISTS emails")

# Create the new emails table with required columns
cursor.execute("""
CREATE TABLE emails (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_email TEXT NOT NULL,
    email_text TEXT NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
)
""")

conn.commit()
conn.close()

print("✅ emails table dropped and recreated successfully.")


