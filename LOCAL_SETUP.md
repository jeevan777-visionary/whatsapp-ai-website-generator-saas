# Local Setup Guide

## Prerequisites
- Python 3.11+
- Redis (optional if `SYNC_TASKS=true`)
- Twilio account (WhatsApp Sandbox)
- Groq API key
- Netlify personal access token

## Installation
```bash
git clone <repo>
cd "Whatsapp ai generator"
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env
```

## Environment Variables
| Variable | Description |
|---|---|
| `TWILIO_ACCOUNT_SID` | Twilio account SID |
| `TWILIO_AUTH_TOKEN` | Twilio auth token |
| `TWILIO_WHATSAPP_NUMBER` | `whatsapp:+14155238886` sandbox |
| `WEBHOOK_URL` | Public URL for Twilio webhook |
| `GROQ_API_KEY` | Groq API key |
| `GROQ_MODEL` | e.g. `llama-3.1-70b-versatile` |
| `NETLIFY_AUTH_TOKEN` | Netlify deploy token |
| `REDIS_URL` | `redis://localhost:6379/0` |
| `DATABASE_URL` | `sqlite:///app.db` |
| `SYNC_TASKS` | `true` for local without Celery |
| `PORT` | Flask port (default 5000) |
| `DEBUG` | `true` for dev |

## Redis Setup
### Windows (Docker)
```bash
docker run -d -p 6379:6379 redis:7-alpine
```

### macOS/Linux
```bash
redis-server
```

## ngrok Setup
```bash
ngrok http 5000
```
Copy HTTPS URL into Twilio Sandbox webhook:
`POST https://<subdomain>.ngrok-free.app/webhook/whatsapp`

## Twilio Setup
1. Enable WhatsApp Sandbox in Twilio Console.
2. Join sandbox from your phone.
3. Configure incoming message webhook URL.

## Groq Setup
1. Create API key at https://console.groq.com
2. Set `GROQ_API_KEY` and `GROQ_MODEL` in `.env`

## Netlify Setup
1. Create personal access token.
2. Set `NETLIFY_AUTH_TOKEN` in `.env`
3. Deployments create sites like `bella-italia-<suffix>.netlify.app`

## Run Locally
Terminal 1:
```bash
python app.py
```

Terminal 2 (if `SYNC_TASKS=false`):
```bash
celery -A app.celery_app worker --loglevel=info
```

Terminal 3 (Frontend):
```bash
cd frontend
npm install
copy .env.example .env
npm run dev
```

## Docker Local
```bash
docker compose up --build
```

## Troubleshooting
| Issue | Fix |
|---|---|
| Webhook 403 | Set `DEBUG=true` or configure valid Twilio signature URL |
| Tasks not running | Start Redis + Celery or set `SYNC_TASKS=true` |
| No live URL | Verify `NETLIFY_AUTH_TOKEN` |
| AI fallback only | Verify `GROQ_API_KEY` |
| Dashboard empty | Send at least one WhatsApp request |

## Verify
```bash
pytest -q
curl http://localhost:5000/health
```
