import asyncio
import aiohttp
import json
import os

CACHE_PATH = "data/kbli2020_cache.json"
BPS_API_KEY = "e613137eb4bc4217c97af7cbbf61ccae"

async def fetch_page(session, page):
    url = "https://webapi.bps.go.id/v1/api/list"
    params = {
        "model": "kbli2020",
        "page": page,
        "per_page": 10,
        "key": BPS_API_KEY,
    }
    try:
        async with session.get(url, params=params, timeout=20) as resp:
            data = await resp.json()
            if data.get("status") != "OK" or "data" not in data:
                print(f"[BPS] Invalid page {page}")
                return []
            return [e["_source"] for e in data["data"][1]]
    except Exception as e:
        print(f"[BPS] Error page {page}: {e}")
        return []

async def fetch_all_pages(total_pages=271, concurrency=5):
    print(f"[BPS] Starting async fetch for {total_pages} pages...")
    all_entries = []
    connector = aiohttp.TCPConnector(limit=concurrency)
    async with aiohttp.ClientSession(connector=connector) as session:
        # Process in batches of 'concurrency'
        for batch_start in range(1, total_pages + 1, concurrency):
            tasks = [
                fetch_page(session, p)
                for p in range(batch_start, min(batch_start + concurrency, total_pages + 1))
            ]
            batch_results = await asyncio.gather(*tasks)
            for r in batch_results:
                all_entries.extend(r)
            print(f"[BPS] Fetched up to page {batch_start + concurrency - 1}, total so far: {len(all_entries)}")
    return all_entries

def load_kbli_from_cache(force_refresh=False):
    if not force_refresh and os.path.exists(CACHE_PATH):
        with open(CACHE_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
        print(f"[INFO] Loaded {len(data)} KBLI entries from cache.")
        return data

    print("[INFO] Fetching fresh KBLI data from BPS WebAPI (async mode)...")
    all_entries = asyncio.run(fetch_all_pages())
    print(f"[BPS] Done. Total fetched: {len(all_entries)} KBLI records.")

    os.makedirs(os.path.dirname(CACHE_PATH), exist_ok=True)
    with open(CACHE_PATH, "w", encoding="utf-8") as f:
        json.dump(all_entries, f, ensure_ascii=False, indent=2)
    print(f"[INFO] Cached {len(all_entries)} entries to {CACHE_PATH}.")
    return all_entries

# --- for standalone testing ---
if __name__ == "__main__":
    print("[DEBUG] Manual run started...")
    data = load_kbli_from_cache(force_refresh=True)
    print(f"[DEBUG] Total KBLI fetched: {len(data)} entries")
