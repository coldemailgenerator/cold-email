import sqlite3

conn = sqlite3.connect("users.db")
cursor = conn.cursor()

cursor.execute("ALTER TABLE emails ADD COLUMN is_locked INTEGER DEFAULT 0")
conn.commit()
conn.close()

print("✅ is_locked column added.")
