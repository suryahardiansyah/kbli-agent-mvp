# simple_waha_bot.py
from fastapi import FastAPI, Request
import requests, time

WAHA_URL = "http://localhost:3000"
SESSION  = "default"
API_WHATSAPP = "http://localhost:8000/webhook/whatsapp"
API_FEEDBACK = "http://localhost:8000/feedback"

app = FastAPI()
STATE = {}  # chat_id -> {"awaiting":"confirm|reason|detail", "input":str, "top1":dict}

def send_text(chat_id, text):
    formatted = text.replace("\\n", "\n").strip()
    payload = {"session": SESSION, "chatId": chat_id, "text": formatted}
    r = requests.post(f"{WAHA_URL}/api/sendText", json=payload,
        headers={"Content-Type":"application/json", "X-API-Key": "mysecret"},
        timeout=30)
    print("sendText:", r.status_code, formatted)

def send_buttons(chat_id, text, buttons, footer=None):
    payload = {
        "session": SESSION,
        "chatId": chat_id,
        "body": text,
        "buttons": [{"id": b["id"], "text": b["text"]} for b in buttons],
    }
    if footer:
        payload["footer"] = footer

    r = requests.post(
        f"{WAHA_URL}/api/sendInteractiveButtons",
        json=payload,
        headers={"Content-Type": "application/json", "X-API-Key": "mysecret"},
        timeout=30,
    )
    print("sendInteractiveButtons:", r.status_code, r.text)

@app.get("/health")
def health(): return {"ok": True}

async def _handle(req: Request):
    evt = await req.json()
    print("Incoming:", evt)
    data = evt.get("payload") or {}
    if data.get("fromMe"): return {"ok": True}

    chat_id = data.get("from") or data.get("chatId")
    text_in = ((data.get("text") or "") or (data.get("message") or "") or
               (data.get("body") or "") or (data.get("content") or "") or
               (data.get("caption") or "")).strip()
    if not chat_id: return {"ok": False, "reason":"no chatId"}

    st = STATE.get(chat_id)
    # feedback confirm
    if st and st.get("awaiting")=="confirm":
        low=text_in.lower()
        if low in {"sesuai","sesuai ✅"}:
            try:
                requests.post(API_FEEDBACK, json={"ts":int(time.time()),"chat_id":chat_id,
                    "type":"confirm_ok","input":st["input"],"predicted_top1":st["top1"]}, timeout=15)
            except: pass
            STATE.pop(chat_id, None); send_text(chat_id,"Siap! Terima kasih 🙏"); return {"ok":True}
        if low in {"tidak sesuai","tidak sesuai ❌"}:
            STATE[chat_id]["awaiting"]="reason"
            send_buttons(chat_id, "Boleh pilih alasannya:", [
                {"id":"r1","text":"Deskripsi KBLI tidak pas"},
                {"id":"r2","text":"Sektor/jenis usaha salah"},
                {"id":"r3","text":"Skala usaha berbeda"},
                {"id":"r4","text":"Lainnya…"},
            ], footer="Bantu tingkatkan akurasi")
            return {"ok":True}

    if st and st.get("awaiting")=="reason":
        t=text_in.lower()
        mapping={"deskripsi kbli tidak pas":"r1","sektor/jenis usaha salah":"r2","skala usaha berbeda":"r3","lainnya…":"r4","lainnya":"r4"}
        sel = next((k for k in mapping if k in t), None)
        if sel=="lainnya…" or sel=="lainnya":
            STATE[chat_id]["awaiting"]="detail"; send_text(chat_id,"Tulis alasannya singkat ya 🙏"); return {"ok":True}
        if sel:
            try:
                requests.post(API_FEEDBACK, json={"ts":int(time.time()),"chat_id":chat_id,
                    "type":"dispute_fixed_reason","reason":sel,"input":st["input"],"predicted_top1":st["top1"]}, timeout=15)
            except: pass
            STATE.pop(chat_id, None); send_text(chat_id,"Catat. Terima kasih 🙏"); return {"ok":True}
        # ulangkan tombol
        send_buttons(chat_id, "Pilih alasan singkat:", [
            {"id":"r1","text":"Deskripsi KBLI tidak pas"},
            {"id":"r2","text":"Sektor/jenis usaha salah"},
            {"id":"r3","text":"Skala usaha berbeda"},
            {"id":"r4","text":"Lainnya…"},
        ]); return {"ok":True}

    if st and st.get("awaiting")=="detail":
        try:
            requests.post(API_FEEDBACK, json={"ts":int(time.time()),"chat_id":chat_id,
                "type":"dispute_free_text","detail":text_in,"input":st["input"],"predicted_top1":st["top1"]}, timeout=15)
        except: pass
        STATE.pop(chat_id, None); send_text(chat_id,"Siap, terima kasih 🙏"); return {"ok":True}

    # normal start/classify
    if not text_in or text_in.lower() in {"start","mulai","halo","hai","hi"}:
        send_text(chat_id, "Halo! 👋\nKetik *deskripsi usaha* 1–2 kalimat.\nContoh: *Menjual pinang dari kebun sendiri, dijajakan di kios pinggir jalan.*")
        return {"ok":True}

    try:
        ai = requests.post(API_WHATSAPP, json={"text": text_in}, timeout=45)
        data_ai = ai.json() if ai.ok else {"reply": f"Gagal (kode {ai.status_code})"}
    except Exception as e:
        data_ai={"reply": f"Error panggil API: {e}"}

    kbli_info = data_ai.get("final_choice", {})
    kode = kbli_info.get("code", "—")
    judul = kbli_info.get("title", "(judul tidak ditemukan)")
    ringkasan = kbli_info.get("desc", "").replace("\n", " ")

    reply = (
        f"📘 *Hasil KBLI Agent*\n\n"
        f"💬 *Input:* {text_in}\n\n"
        f"🏷️ *Final KBLI:* {kode}\n"
        f"{judul}\n\n"
        f"📄 _{ringkasan}_\n\n"
        f"Apakah hasil ini *sesuai* dengan deskripsi usahamu?"
    )
    send_text(chat_id, reply)


    STATE[chat_id] = {"awaiting":"confirm","input":text_in,"top1":data_ai.get("final_choice",{})}
    send_buttons(chat_id, "Apakah hasil ini *sesuai*?",
        [{"id":"yes","text":"Sesuai ✅"},{"id":"no","text":"Tidak sesuai ❌"}],
        footer="Feedback 2-tap, tanpa ngetik panjang")
    return {"ok":True}

@app.post("/waha-webhook")
async def waha_webhook(req: Request): return await _handle(req)

@app.post("/waha-webhook/")
async def waha_webhook_slash(req: Request): return await _handle(req)
