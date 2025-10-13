from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from src.classifier import classify_query
from src.loader_bps import load_kbli_from_cache
import os
import datetime

# ==========================================================
#   KBLI Agent API - FastAPI Server
# ==========================================================

app = FastAPI(
    title="KBLI Agent MVP",
    description="API minimal untuk klasifikasi KBLI dari teks deskriptif usaha",
    version="0.3.0"
)

ADMIN_REFRESH_KEY = os.getenv("ADMIN_REFRESH_KEY", "YOUR_SECRET_REFRESH_KEY")  # Change this to your secret key


# ----------------------------------------------------------
# Root endpoint
# ----------------------------------------------------------
@app.get("/")
def root():
    return {
        "message": "✅ KBLI Agent API aktif.",
        "usage": "/classify?query=deskripsi_usaha",
        "refresh": "/refresh?key=YOUR_SECRET_REFRESH_KEY"
    }


# ----------------------------------------------------------
# Main classifier endpoint
# ----------------------------------------------------------
@app.get("/classify")
def classify(query: str = Query(..., description="Deskripsi usaha atau pekerjaan")):
    try:
        result = classify_query(query)
        return JSONResponse(content=result)
    except Exception as e:
        print("[ERROR] classify():", e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


# ----------------------------------------------------------
# Force refresh KBLI cache (Admin only)
# ----------------------------------------------------------
@app.get("/refresh")
def refresh_cache(key: str):
    """
    Gunakan /refresh?key=YOUR_SECRET_REFRESH_KEY untuk memaksa pembaruan KBLI dari BPS.
    """
    if key != ADMIN_REFRESH_KEY:
        return JSONResponse(content={"error": "Unauthorized"}, status_code=401)

    try:
        data = load_kbli_from_cache(force_refresh=True)

        # Tambahkan timestamp untuk mencatat waktu update terakhir
        update_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Simpan metadata update
        with open("data/last_refresh.txt", "w", encoding="utf-8") as f:
            f.write(f"Last refresh: {update_time}, total entries: {len(data)}\n")

        return JSONResponse(
            content={
                "status": "success",
                "refreshed_at": update_time,
                "count": len(data)
            }
        )
    except Exception as e:
        print("[ERROR] refresh_cache():", e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


# ----------------------------------------------------------
# Webhook endpoint (optional - for WhatsApp / n8n integration)
# ----------------------------------------------------------
@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Endpoint opsional untuk menerima webhook dari n8n / WhatsApp Business API.
    """
    try:
        payload = await request.json()
        user_message = payload.get("text") or payload.get("message") or ""
        if not user_message:
            return PlainTextResponse("No message received", status_code=400)

        result = classify_query(user_message)
        response_text = (
            f"*Hasil KBLI Agent:*\n\n"
            f"Input: {result['query']}\n\n"
            f"*Final KBLI:* {result['final_choice']}\n\n"
            f"{result['reasoning']}\n\n"
            f"(MVP versi awal - hasil masih eksperimental)"
        )
        return JSONResponse(content={"reply": response_text})

    except Exception as e:
        print("[ERROR] whatsapp_webhook():", e)
        return JSONResponse(content={"error": str(e)}, status_code=500)


# ----------------------------------------------------------
# Entry point (if run manually)
# ----------------------------------------------------------
if __name__ == "__main__":
    import uvicorn
    print("============================================")
    print("  Starting KBLI Agent API (FastAPI + Uvicorn)")
    print("============================================")
    if not os.path.exists("venv"):
        print("[WARN] No venv found, using system Python.")
    uvicorn.run("src.api_handler:app", host="0.0.0.0", port=8000, reload=True)
