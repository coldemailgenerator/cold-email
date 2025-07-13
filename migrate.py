import sqlite3

def add_lock_password_column():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()

    # Check if column already exists
    cursor.execute("PRAGMA table_info(users)")
    columns = [col[1] for col in cursor.fetchall()]

    if 'lock_password' not in columns:
        cursor.execute("ALTER TABLE users ADD COLUMN lock_password TEXT DEFAULT ''")
        print("✅ 'lock_password' column added.")
    else:
        print("ℹ️ 'lock_password' column already exists.")

    conn.commit()
    conn.close()

add_lock_password_column()
