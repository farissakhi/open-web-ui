import sqlite3
import os

db_path = r'D:\PENTING\open-webui-main\backend\data\webui.db'

print("=== CLEANING KNOWLEDGE BASE ===\n")

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 1. List current knowledge
cursor.execute("SELECT id, name FROM knowledge")
knowledges = cursor.fetchall()
print(f"Current knowledge bases ({len(knowledges)}):")
for k in knowledges:
    print(f"  - ID: {k[0]}, Name: {k[1]}")

# 2. List files
cursor.execute("SELECT id, filename FROM file")
files = cursor.fetchall()
print(f"\nCurrent files ({len(files)}):")
for f in files:
    print(f"  - {f[1]}")

# 3. Delete all knowledge and knowledge_file entries
print("\n--- Deleting knowledge entries ---")
cursor.execute("DELETE FROM knowledge_file")
print(f"Deleted {cursor.rowcount} knowledge_file entries")

cursor.execute("DELETE FROM knowledge")
print(f"Deleted {cursor.rowcount} knowledge entries")

conn.commit()
print("\n✅ Knowledge base cleaned!")

# Verify
cursor.execute("SELECT COUNT(*) FROM knowledge")
print(f"\nVerification - Knowledge count: {cursor.fetchone()[0]}")

cursor.execute("SELECT COUNT(*) FROM knowledge_file")
print(f"Verification - Knowledge_file count: {cursor.fetchone()[0]}")

conn.close()
print("\nDone! Now restart backend and re-upload documents.")
