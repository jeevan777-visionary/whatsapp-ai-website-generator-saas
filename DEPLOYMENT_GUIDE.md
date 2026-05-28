# Deployment Guide

## Production Architecture
- Flask API (`web` service)
- Celery worker (`worker` service)
- Redis broker
- SQLite/Postgres persistence
- Netlify static hosting for generated websites

## Docker Production
```bash
docker compose up --build -d
```

Services:
- `web` on port `5000`
- `worker` Celery consumer
- `redis` queue broker

## Manual Production Run
```bash
export SYNC_TASKS=false
export REDIS_URL=redis://localhost:6379/0
python app.py
celery -A app.celery_app worker --loglevel=info
```

## Deploying the SaaS UI
- Recommended: deploy `frontend/` to Vercel (Next.js).
- Backend/worker: deploy Flask to Render/Railway.
- Ensure `NEXT_PUBLIC_API_URL` in Vercel points to your backend base URL.

## Netlify Automatic Deployment Flow
1. Website files generated in `generated_sites/<request_id>/`
2. ZIP archive created
3. Netlify site created with slug `business-name-<suffix>`
4. ZIP uploaded as deploy
5. Deploy polled until `ready`
6. Live URL stored in SQLite and sent to WhatsApp

## Deployment Commands
```bash
# Health
curl https://<your-domain>/health

# Dashboard
open https://<your-domain>/dashboard/

# Download generated zip
curl -O https://<your-domain>/dashboard/download/<request_id>

# Preview generated site
open https://<your-domain>/dashboard/preview/<request_id>
```

## Twilio Webhook (Production)
Set webhook to:
`https://<your-domain>/webhook/whatsapp`

## Environment Checklist
- [ ] `NETLIFY_AUTH_TOKEN` configured
- [ ] `GROQ_API_KEY` configured
- [ ] Twilio credentials configured
- [ ] Redis reachable from worker
- [ ] Public HTTPS URL for webhook

## Rollback
Use `deployment/rollback.py` with `site_id` and previous `deploy_id` from deployment logs.

## Custom Domains
Use `deployment/domain_hooks.py`:
```python
map_custom_domain(site_id, "www.yourdomain.com")
```

## CI/CD
GitHub Actions runs tests and compile checks on push.

## Monitoring
- Dashboard: `/dashboard/deployments`
- Logs: stdout JSON-like log lines from Flask/Celery
- DB tables: `deployment_logs`, `deployment_statuses`, `analytics_events`
