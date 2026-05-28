# Quickstart

## 1. Install
```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## 2. Configure `.env`
Set at minimum:
- `GROQ_API_KEY`
- `NETLIFY_AUTH_TOKEN`
- `TWILIO_ACCOUNT_SID`, `TWILIO_AUTH_TOKEN`, `TWILIO_WHATSAPP_NUMBER`
- `JWT_SECRET`

For local task execution without Redis:
```env
SYNC_TASKS=true
```

## 3. Run API
```bash
python app.py
```

## 4. Run Worker (if not using SYNC_TASKS)
```bash
celery -A app.celery_app worker --loglevel=info
```

## 4.1 Run Frontend (Next.js)
1. Install:
   ```bash
   cd frontend
   npm install
   copy .env.example .env
   ```
2. Start:
   ```bash
   npm run dev
   ```
3. Open:
   - http://localhost:3000

## 5. Expose Webhook (ngrok)
```bash
ngrok http 5000
```
Set Twilio webhook to: `https://<ngrok-id>.ngrok.io/webhook/whatsapp`

## 6. Test WhatsApp Flow
Send:
```text
Build a modern luxury restaurant website for Bella Italia with online reservations
```

You will receive:
1. Generating message
2. Deploying message
3. Live Netlify URL

## 7. Open Dashboard
http://localhost:5000/dashboard/

## 8. Run Full SaaS Stack (Frontend + FastAPI + Flask + Worker + Redis + PostgreSQL)
```bash
docker compose up --build
```

Open:
- Frontend SaaS UI: `http://localhost:3000`
- Flask backend: `http://localhost:5000`
- FastAPI backend/docs: `http://localhost:8000/docs`
