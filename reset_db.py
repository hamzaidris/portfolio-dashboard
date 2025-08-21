import os
from trackerbazaar.data import init_db, DB_FILE

if os.path.exists(DB_FILE):
    print(f"Deleting old database: {DB_FILE}")
    os.remove(DB_FILE)

print("Recreating database schema...")
init_db()
print("✅ Database has been reset successfully!")
