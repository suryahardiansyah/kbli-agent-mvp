import sqlite3
import os

def load_kbli_from_sqlite(db_path="data/baku.db", table="kbli2020"):
    """
    Loads KBLI 2020 data from the SIBAKU Mobile SQLite database.

    - Reads from the specified table (default: kbli2020)
    - Keeps only rows with 5-digit numeric KBLI codes
    - Returns a list of dictionaries: [{kbli, judul, deskripsi}, ...]
    """
    if not os.path.exists(db_path):
        raise FileNotFoundError(f"Database file not found: {db_path}")

    conn = sqlite3.connect(db_path)
    cur = conn.cursor()

    try:
        # Ensure table exists
        cur.execute("SELECT name FROM sqlite_master WHERE type='table' AND name=?", (table,))
        exists = cur.fetchone()
        if not exists:
            raise ValueError(f"Table '{table}' not found in database {db_path}")

        # Attempt to read data
        cur.execute(f"SELECT kode, judul, deskripsi FROM {table}")
        rows = cur.fetchall()

        data = []
        seen_codes = set()

        for kode, judul, deskripsi in rows:
            if not kode:
                continue

            kode = str(kode).strip()
            if len(kode) == 5 and kode.isdigit():
                # Handle None values gracefully
                judul = (judul or "").strip()
                deskripsi = (deskripsi or "").strip()

                # Avoid duplicates
                if kode not in seen_codes:
                    seen_codes.add(kode)
                    data.append({
                        "kbli": kode,
                        "judul": judul,
                        "deskripsi": deskripsi
                    })

        print(f"[INFO] Loaded {len(data)} valid 5-digit KBLI entries from '{table}'.")
        return data

    except sqlite3.OperationalError as e:
        raise RuntimeError(f"Failed to load data from table '{table}': {e}")

    finally:
        conn.close()
