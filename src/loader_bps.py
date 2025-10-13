import asyncio
import aiohttp
import json
import os
from datetime import datetime

# === Configuration ===
CACHE_PATH = "data/kbli2020_cache.json"
BPS_API_KEY = "e613137eb4bc4217c97af7cbbf61ccae"
BPS_API_URL = "https://webapi.bps.go.id/v1/api/list"


# === Async fetch per page ===
async def fetch_page(session, page, per_page=10):
    params = {
        "model": "kbli2020",
        "page": page,
        "per_page": per_page,
        "key": BPS_API_KEY,
    }
    try:
        async with session.get(BPS_API_URL, params=params, timeout=30) as resp:
            if resp.status != 200:
                print(f"[BPS] HTTP error {resp.status} on page {page}")
                return []

            data = await resp.json()
            if data.get("status") != "OK" or "data" not in data:
                print(f"[BPS] Invalid or missing data on page {page}")
                return []

            entries = data["data"][1]
            cleaned = []
            for e in entries:
                src = e.get("_source", {})
                cleaned.append({
                    "kbli": src.get("id", ""),
                    "kode": src.get("id", "").split("_")[-1],
                    "judul": src.get("judul", "").strip(),
                    "deskripsi": src.get("deskripsi", "").strip(),
                    "level": src.get("level", ""),
                    "url": src.get("url", ""),
                })
            return cleaned

    except Exception as e:
        print(f"[BPS] Error page {page}: {e}")
        return []


# === Async gather for all pages ===
async def fetch_all_pages(total_pages=271, concurrency=10):
    print(f"[BPS] Starting async fetch for {total_pages} pages...")
    all_entries = []
    connector = aiohttp.TCPConnector(limit=concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        for batch_start in range(1, total_pages + 1, concurrency):
            batch_end = min(batch_start + concurrency - 1, total_pages)
            tasks = [fetch_page(session, p) for p in range(batch_start, batch_end + 1)]
            batch_results = await asyncio.gather(*tasks)
            for r in batch_results:
                all_entries.extend(r)
            print(f"[BPS] Fetched up to page {batch_end}, total so far: {len(all_entries)}")

    return all_entries


# === Cache handler ===
def load_kbli_from_cache(force_refresh=False):
    # --- Load from cache if available ---
    if not force_refresh and os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            cached = json.load(f)

        # Backward compatibility: support old format (just list)
        if isinstance(cached, list):
            data = cached
            last_updated = "unknown (legacy cache)"
        else:
            data = cached.get("data", [])
            last_updated = cached.get("last_updated", "unknown")

        print(f"[INFO] Loaded {len(data)} KBLI entries from cache (last updated: {last_updated}).")
        return data

    # --- Fetch new data ---
    print("[INFO] Fetching fresh KBLI data from BPS WebAPI (async mode)...")
    all_entries = asyncio.run(fetch_all_pages())
    print(f"[BPS] Done. Total fetched: {len(all_entries)} KBLI records.")

    # --- Save new cache with metadata ---
    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    cache_obj = {
        "last_updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "source": "BPS WebAPI",
        "model": "kbli2020",
        "data": all_entries,
    }

    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(cache_obj, f, ensure_ascii=False, indent=2)

    print(f"[INFO] Cached {len(all_entries)} entries to {CACHE_PATH}.")
    return all_entries


# === Standalone test mode ===
if __name__ == "__main__":
    print("[DEBUG] Manual run started...")
    data = load_kbli_from_cache(force_refresh=True)
    print(f"[DEBUG] Total KBLI fetched: {len(data)} entries")
