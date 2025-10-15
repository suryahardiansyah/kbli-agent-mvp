# api_handler.py
# -*- coding: utf-8 -*-
from fastapi import FastAPI, Query
from fastapi.responses import JSONResponse, PlainTextResponse
from pydantic import BaseModel
from typing import Dict, Any, Optional
import os, json, time
from .classifier import classify_query, Preprocessor

app = FastAPI(title="KBLI Agent API", version="clean")
_pre = Preprocessor()

DATA_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
FEEDBACK_PATH = os.path.join(DATA_DIR, "user_feedback.jsonl")
os.makedirs(DATA_DIR, exist_ok=True)

class ClassifyResponse(BaseModel):
    query: str
    final_choice: Dict[str, Any]
    recommendations: Optional[list] = None
    reasoning: Optional[str] = None

class WhatsAppInbound(BaseModel):
    text: str

@app.get("/", response_class=PlainTextResponse)
def root():
    return "KBLI Agent API OK: /classify , /webhook/whatsapp , /feedback"

@app.get("/classify", response_model=ClassifyResponse)
def classify(query: str = Query(..., description="deskripsi usaha bahasa Indonesia")):
    clean = (_pre(query) if query else "").strip()
    return JSONResponse(classify_query(clean))

@app.post("/webhook/whatsapp")
def whatsapp_webhook(body: WhatsAppInbound):
    # 1) Normalisasi input
    raw = body.text or ""
    clean = _pre(raw) if raw else ""

    # 2) Panggil classifier
    result = classify_query(clean)  # -> {query, final_choice, recommendations, reasoning}
    top = (result.get("final_choice") or {}) if isinstance(result, dict) else {}

    # 3) Normalisasi field agar konsisten utk WhatsApp & bot
    code = top.get("kode") or top.get("kbli") or top.get("code") or "-"
    title = top.get("judul") or top.get("title") or "(judul tidak ditemukan)"
    desc = top.get("deskripsi") or top.get("desc") or ""
    desc = (desc or "").strip()

    final_choice = {
        "code": code,
        "title": title,
        "desc": desc,
        "score": float(top.get("score", 0.0)) if isinstance(top.get("score", 0.0), (int, float)) else 0.0,
    }

    # 4) Format balasan rapi (teks untuk fallback)
    snippet = desc.replace("\n", " ").strip()
    if len(snippet) > 600:
        snippet = snippet[:600] + "…"

    reply = (
        "📘 *Hasil KBLI Agent*\n\n"
        f"💬 *Input:* {raw}\n\n"
        f"🏷️ *Final KBLI:* {code}\n"
        f"{title}\n\n"
        f"📄 _{snippet or '—'}_\n\n"
        "Apakah hasil ini *sesuai* dengan deskripsi usahamu?"
    )

    # 5) Kembalikan TEKS + OBJEK (dipakai bot)
    return {"reply": reply, "final_choice": final_choice}


@app.post("/feedback")
def feedback_sink(payload: Dict[str, Any]):
    with open(FEEDBACK_PATH, "a", encoding="utf-8") as f:
        f.write(json.dumps(payload, ensure_ascii=False) + "\n")
    return {"ok": True, "saved": True, "ts": int(time.time())}
