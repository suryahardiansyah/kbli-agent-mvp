from .retriever import retrieve_kbli
from .classifier import classify_query

@app.post("/webhook/whatsapp")
async def classify(req: Request):
    data = await req.json()
    text = data.get("text", "").strip()

    # 1️⃣ Retrieve candidates
    candidates = retrieve_kbli(text)

    # 2️⃣ Run classifier (or similarity ranking)
    choice = classify_text(text, candidates)

    reply = (
        f"📘 Hasil KBLI Agent\n\n"
        f"💬 Input: {text}\n"
        f"🏷️ Final KBLI: {choice['code']}\n"
        f"📄 {choice['description']}\n\n"
        f"Setelah dicek, apakah kira-kira jawaban saya tepat?"
    )
    return {"reply": reply, "final_choice": choice}
