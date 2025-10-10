from fastapi import FastAPI, Query, Request
from fastapi.responses import JSONResponse, PlainTextResponse
from classifier import classify_query

app = FastAPI(
    title="KBLI Agent MVP",
    description="API minimal untuk klasifikasi KBLI dari teks deskriptif usaha",
    version="0.2.0"
)

@app.get("/")
def root():
    return {"message": "KBLI Agent API aktif. Gunakan endpoint /classify?query=..."}

@app.get("/classify")
def classify(query: str = Query(..., description="Deskripsi usaha atau pekerjaan")):
    """
    Endpoint utama untuk menerima deskripsi teks dan mengembalikan hasil klasifikasi KBLI.
    """
    try:
        result = classify_query(query)
        return JSONResponse(content=result)
    except Exception as e:
        print("[ERROR] classify():", e)
        return JSONResponse(content={"error": str(e)}, status_code=500)

from loader_bps import load_kbli_from_cache

ADMIN_REFRESH_KEY = "YOUR_SECRET_REFRESH_KEY"  # choose a random secret

@app.get("/refresh")
def refresh_cache(key: str):
    if key != ADMIN_REFRESH_KEY:
        return JSONResponse(content={"error": "Unauthorized"}, status_code=401)
    try:
        data = load_kbli_from_cache(force_refresh=True)
        return JSONResponse(content={"status": "success", "count": len(data)})
    except Exception as e:
        return JSONResponse(content={"error": str(e)}, status_code=500)

@app.post("/webhook/whatsapp")
async def whatsapp_webhook(request: Request):
    """
    Endpoint opsional untuk menerima webhook langsung dari n8n / WhatsApp Business.
    """
    try:
        payload = await request.json()
        user_message = payload.get("text") or payload.get("message") or ""
        if not user_message:
            return PlainTextResponse("No message received", status_code=400)

        result = classify_query(user_message)
        # format singkat agar cocok dibalas via WA
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

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("api_handler:app", host="0.0.0.0", port=8000, reload=True)
