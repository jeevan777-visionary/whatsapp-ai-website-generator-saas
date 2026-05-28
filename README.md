# WhatsApp AI Website Generator

Production-grade automation platform that turns WhatsApp messages into deployed websites using Flask + FastAPI, Celery, Groq Llama 3, PostgreSQL/SQLite, and Netlify.

## Features
- Twilio WhatsApp webhook ingestion (text + voice notes)
- AI requirement extraction and premium content generation
- Multi-template static site generation (restaurant, portfolio, store, blog, agency, SaaS)
- Automatic Netlify deployment with live public URLs
- Admin analytics dashboard with real-time progress tracking
- Website edit commands over WhatsApp
- Multi-language bot responses (EN/ES/FR)
- AI logo SVG generation
- Async Celery + Redis pipeline (or sync local mode)
- SQLite persistence, deployment logs, analytics, edit history
- Docker + GitHub Actions CI
- Next.js TypeScript SaaS frontend (landing, auth, dashboard, builder, editor, deployments)
- FastAPI v2 backend with JWT and WebSocket progress APIs

## Quick Links
- [QUICKSTART.md](QUICKSTART.md)
- [LOCAL_SETUP.md](LOCAL_SETUP.md)
- [DEPLOYMENT_GUIDE.md](DEPLOYMENT_GUIDE.md)
- [docs/ARCHITECTURE.md](docs/ARCHITECTURE.md)

## Run Locally
```bash
pip install -r requirements.txt
copy .env.example .env
# set SYNC_TASKS=true for no-Redis local mode
python app.py
```

Worker (production/async mode):
```bash
celery -A app.celery_app worker --loglevel=info
```

Docker:
```bash
docker compose up --build
```

## Dashboard
- http://localhost:5000/dashboard/
- Gallery, deployment tracker, preview, ZIP download

## SaaS Frontend + API
- Next.js app: `http://localhost:3000`
- FastAPI docs: `http://localhost:8000/docs`
- Flask API + webhook runtime: `http://localhost:5000`

## WhatsApp Examples
**New site:**
```text
Build a modern luxury restaurant website for Bella Italia with online reservations
```

**Edit commands:**
```text
Make the header blue
Add testimonials section
Switch template restaurant
```

## Environment Variables
See `.env.example` for full list including:
- `TWILIO_*`, `GROQ_*`, `NETLIFY_AUTH_TOKEN`
- `REDIS_URL`, `DATABASE_URL`, `SYNC_TASKS`

## Testing
```bash
pytest -q
```

## Deployment Output
After successful generation, users receive:
```text
✅ Your website is live: https://bella-italia-<id>.netlify.app
```

## Architecture
WhatsApp → Twilio Webhook → Flask → Celery → AI → Generator → Netlify → Live URL → WhatsApp
