# simple_waha_bot.py (minimal, no-feedback)
from fastapi import FastAPI, Request
import os, requests, textwrap

# --- Config (override via env if you want) ---
WAHA_URL      = os.getenv("WAHA_URL", "http://localhost:3000")
WAHA_API_KEY  = os.getenv("WAHA_API_KEY", "mysecret")
SESSION       = os.getenv("WAHA_SESSION", "default")
API_CLASSIFY  = os.getenv("API_CLASSIFY", "http://localhost:8000/classify")   # e.g. https://rude-lonelily-benito.ngrok-free.dev/classify

app = FastAPI()

def _clean(s: str, limit: int = 600) -> str:
    s = (s or "").replace("\r", " ").replace("\n", " ").strip()
    s = " ".join(s.split())
    return s[:limit].rstrip()

def send_text(chat_id: str, text: str) -> None:
    payload = {"session": SESSION, "chatId": chat_id, "text": text.strip()}
    try:
        r = requests.post(
            f"{WAHA_URL}/api/sendText",
            json=payload,
            headers={"Content-Type": "application/json", "X-API-Key": WAHA_API_KEY},
            timeout=30,
        )
        print("sendText:", r.status_code)
    except Exception as e:
        print("sendText error:", e)

@app.get("/health")
def health():
    return {"ok": True}

def _pick_text(d: dict) -> str:
    # WAHA can deliver text under different keys
    for k in ("text", "message", "body", "content", "caption"):
        v = (d.get(k) or "").strip()
        if v:
            return v
    return ""

def _extract_kbli(result: dict):
    """
    Accepts various shapes:
      - {"final_choice":{"code","title|name","desc|description"}}
      - {"kbli":{...}}
      - flat: {"code","title","description"}
      - or {"reply": "..."}  -> will be sent as-is
    """
    if isinstance(result.get("reply"), str) and result["reply"].strip():
        return None, None, None, result["reply"].strip()

    fc = result.get("final_choice") or result.get("kbli") or {}
    code = fc.get("code") or result.get("code") or "—"
    title = (
        fc.get("title")
        or fc.get("name")
        or result.get("title")
        or "Judul tidak ditemukan"
    )
    desc = (
        fc.get("desc")
        or fc.get("description")
        or result.get("description")
        or "Tidak ditemukan"
    )
    return _clean(code), _clean(title), _clean(desc), None

@app.post("/waha-webhook")
@app.post("/waha-webhook/")
async def waha_webhook(req: Request):
    evt = await req.json()
    print("Incoming:", evt)

    data = evt.get("payload") or evt.get("body") or evt
    if not isinstance(data, dict):
        return {"ok": False, "reason": "bad payload"}

    # Ignore our own messages
    if data.get("fromMe"):
        return {"ok": True}

    chat_id = data.get("from") or data.get("chatId")
    if not chat_id:
        return {"ok": False, "reason": "no chatId"}

    text_in = _pick_text(data)
    if not text_in or text_in.lower() in {"start", "mulai", "halo", "hai", "hi"}:
        send_text(
            chat_id,
            "Halo! 👋\nKetik *deskripsi usaha* 1–2 kalimat.\nContoh: *Menjual pinang dari kebun sendiri, dijajakan di kios pinggir jalan.*",
        )
        return {"ok": True}

    # --- Call your classifier (GET /classify?query=...) ---
    try:
        r = requests.get(
            API_CLASSIFY,
            params={"query": text_in},
            headers={"Accept": "application/json"},
            timeout=35,
        )
        result = r.json() if r.ok else {"reply": f"Maaf, API bermasalah (HTTP {r.status_code})."}
    except Exception as e:
        result = {"reply": f"Maaf, API tidak dapat dihubungi: {e}"}

    code, title, desc, direct_reply = _extract_kbli(result)

    if direct_reply:
        # API already returned formatted text
        send_text(chat_id, direct_reply)
        return {"ok": True}

    # --- Compose concise, non-hallucinatory message (no feedback ask) ---
    msg = textwrap.dedent(
        f"""\
        📘 *Hasil KBLI Agent*

        💬 *Input:* {text_in}

        🏷️ *Final KBLI:* {code} — {title}

        📄 _{desc}_"""
    ).strip()

    send_text(chat_id, msg)
    return {"ok": True}
