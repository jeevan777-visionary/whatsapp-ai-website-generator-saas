# Deployment

## Local
```bash
docker compose up --build
```

## Production
- Configure Twilio webhook URL to `/webhook/whatsapp`.
- Set Netlify token and Groq key in environment.
- Run Flask app and Celery worker as separate services.
- Use managed Redis for queue reliability.

## Netlify Process
- Build static package in `generated_sites/<request_id>`.
- Create zip archive.
- Upload through Netlify Sites API.
- Return `ssl_url` to requester via WhatsApp.
