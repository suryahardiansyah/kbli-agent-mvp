import sqlite3
import os

db_path = "data/baku.db"  # adjust path if needed

if not os.path.exists(db_path):
    print(f"[ERROR] Database file not found: {db_path}")
    exit(1)

try:
    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    print("\n=== 📦 TABLES IN DATABASE ===")
    cur.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables = [row[0] for row in cur.fetchall()]
    if not tables:
        print("No tables found.")
        exit(0)

    for t in tables:
        print(f"\n🔹 Table: {t}")
        try:
            # Show columns
            cur.execute(f"PRAGMA table_info({t});")
            cols = [c[1] for c in cur.fetchall()]
            print(f"   Columns: {', '.join(cols)}")

            # Show row count
            cur.execute(f"SELECT COUNT(*) FROM {t};")
            count = cur.fetchone()[0]
            print(f"   Rows: {count}")

            # Show sample data
            cur.execute(f"SELECT * FROM {t} LIMIT 5;")
            rows = cur.fetchall()
            if rows:
                print("   Sample rows:")
                for r in rows:
                    print("     -", r)
            else:
                print("   (No data)")

        except Exception as e:
            print(f"   ⚠️ Error reading table '{t}': {e}")

except Exception as e:
    print(f"[ERROR] Failed to read database: {e}")

finally:
    conn.close()
