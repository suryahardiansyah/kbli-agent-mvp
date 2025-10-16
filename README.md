# KBLI WhatsApp Agent — Local Setup (WAHA + FastAPI Bot)

Runs entirely on your machine:

WhatsApp (phone) ⇄ WAHA (Docker, :3000) ⇄ Bot (FastAPI, :8080) ⇄ KBLI API (FastAPI, :8000)

---

## 0) Prerequisites
- Docker Desktop
- Python 3.10+ (with a virtual environment)
- A WhatsApp account on your phone (to scan QR in WAHA)

Defaults used here:
- WAHA_API_KEY = `mysecret`
- WAHA Dashboard: `http://localhost:3000/dashboard`
- KBLI API: `http://localhost:8000`
- Bot: `http://localhost:8080`

---

## 1) Start WAHA (Docker)

    docker run -d --name waha --restart unless-stopped `
      -p 3000:3000 `
      -e WAHA_API_KEY=mysecret `
      devlikeapro/waha:latest

Open: http://localhost:3000/dashboard

Session setup:
- Create session `default`
- Scan the QR with your WhatsApp
- Wait until status shows **Working**
- Session → Configuration:
  - Webhook URL: `http://host.docker.internal:8080/waha-webhook`
  - Event: `message`
  - Webhook retry (recommended): items = 1, delay = 2s, policy = linear

---

## 2) Start the KBLI API (port 8000)

    cd E:\GitHub\kbli-agent-mvp
    .\.venv\Scripts\Activate.ps1
    uvicorn src.api_handler:app --host 0.0.0.0 --port 8000 --reload

Quick test:

    Invoke-RestMethod -Method Get -Uri "http://localhost:8000/classify?query=pengemudi%20truk"

---

## 3) Start the WAHA Bot (port 8080)
The bot receives WAHA webhooks and replies using the KBLI API (no buttons, no follow-up—just code, title, description).

    cd E:\GitHub\kbli-agent-mvp
    .\.venv\Scripts\Activate.ps1
    uvicorn src.simple_waha_bot:app --host 0.0.0.0 --port 8080 --reload

Health check:

    Invoke-RestMethod -Uri "http://localhost:8080/health"

Now send a WhatsApp message to the number linked in WAHA; you should receive a neat KBLI reply.

---

## 4) (Optional) Use ngrok for the KBLI API

Expose your API publicly (not required for local-only):

    ngrok http 8000

Point the bot to that URL (takes effect after restart):

    setx API_CLASSIFY "https://<your-ngrok-subdomain>.ngrok-free.dev/classify"

Restart the bot process to pick up `API_CLASSIFY`.

---

## Quick Restart Cheat Sheet

    # WAHA
    docker restart waha
    docker logs -f waha

    # KBLI API (Ctrl+C to stop)
    uvicorn src.api_handler:app --host 0.0.0.0 --port 8000 --reload

    # Bot (Ctrl+C to stop)
    uvicorn src.simple_waha_bot:app --host 0.0.0.0 --port 8080 --reload

---

## Troubleshooting

WAHA returns 401 for /api/sendText (or others):
- Ensure WAHA started with `-e WAHA_API_KEY=mysecret`
- The bot includes header `X-API-Key: mysecret` on WAHA API calls

WAHA not hitting your bot (no incoming logs):
- In WAHA session config, Webhook URL must be `http://host.docker.internal:8080/waha-webhook` (not `localhost`)
- Event must include `message`
- Session status must be **Working**; logout + re-scan QR if needed

404 on `/waha-webhook`:
- The bot must be running on port 8080
- Both `/waha-webhook` and `/waha-webhook/` are implemented

Wrong/messy message formatting:
- The bot uses simple WhatsApp-friendly Markdown (`*bold*`, `_italic_`)
- It formats from whatever your KBLI API returns:
  - `final_choice.{code,title|name,desc|description}`
  - `kbli.{code,title|name,desc|description}`
  - flat `code/title/description`
  - or a plain `reply` string (forwarded as-is)

---

## What’s Running
- WAHA — WhatsApp session manager; relays messages to/from your bot
- KBLI API (`src/api_handler.py`) — Classification endpoint (`GET /classify?query=…`)
- Bot (`src.simple_waha_bot.py`) — Glue between WAHA and KBLI API; replies neatly without feedback prompts
