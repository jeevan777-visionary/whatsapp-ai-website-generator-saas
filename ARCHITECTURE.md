# Architecture

## Core Components
- Flask API receives Twilio WhatsApp webhooks.
- Celery worker processes requests asynchronously using Redis broker.
- AI pipeline (Groq Llama 3) extracts requirements and generates premium copy.
- Generator renders Jinja2 + Tailwind templates into static websites.
- Deployment module zips and deploys sites to Netlify.
- SQLite stores users, requests, extraction output, and deployment logs.

## Reliability
- Rate limiting on inbound webhook.
- Retry wrapper for Netlify deployment.
- AI fallback for graceful degradation when API is unavailable.
- Structured logging and status updates back to WhatsApp users.
