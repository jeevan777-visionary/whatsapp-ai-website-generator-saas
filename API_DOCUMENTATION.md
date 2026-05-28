# API Documentation

Base URLs:
- Flask API: `http://localhost:5000`
- FastAPI v2: `http://localhost:8000`

## Health
- `GET /health`

## Authentication (JWT)
- `POST /api/auth/signup`
  - Body: `{ "email": "...", "password": "..." }`
  - Response: `{ "token": "..." }`
- `POST /api/auth/login`
  - Body: `{ "email": "...", "password": "..." }`
  - Response: `{ "token": "..." }`
- `GET /api/auth/me`
  - Header: `Authorization: Bearer <token>`

## Templates
- `GET /api/templates`

## Projects
- `POST /api/projects`
  - Header: `Authorization: Bearer <token>`
  - Body: `{ "message": "Build a restaurant website..." }`
  - Response: `{ "request_id": "...", "status": "queued" }`
- `GET /api/projects`
  - Header: `Authorization: Bearer <token>`
  - Response: list of projects for the signed-in user
- `GET /api/projects/<request_id>`
  - Header: `Authorization: Bearer <token>`
  - Response: project status
- `POST /api/projects/<request_id>/edit`
  - Header: `Authorization: Bearer <token>`
  - Body: `{ "command": "Make the theme blue. Add testimonials." }`

## Preview + Download
- `GET /preview/<request_id>/` (HTML preview, served with assets)
- `GET /preview/<request_id>/<filename>` (assets)
- `GET /api/projects/<request_id>/download`

## Progress WebSocket
- `WS /ws/progress/<request_id>`
  - Sends JSON frames like:
    - `{ "request_id": "...", "phase": "building_site", "progress": 70, "message": "...", "live_url": "..." }`

## FastAPI v2 (Startup SaaS API)
- `POST /api/v2/auth/signup`
- `POST /api/v2/auth/login`
- `GET /api/v2/projects`
- `POST /api/v2/projects`
- `POST /api/v2/projects/{request_id}/edit`
- `GET /api/v2/projects/{request_id}/download`
- `POST /api/v2/settings/language`
- `POST /api/v2/whatsapp/incoming`
- `POST /api/v2/voice/transcribe`
- `WS /ws/v2/progress/{request_id}`

Swagger UI:
- `http://localhost:8000/docs`

## WhatsApp Webhook
- `POST /webhook/whatsapp`
  - Twilio posts `From` and `Body` (and optional audio media fields).
