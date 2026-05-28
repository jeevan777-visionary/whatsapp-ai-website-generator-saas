# Troubleshooting

## 1) Webhook returns `403 Invalid signature`
- Ensure Twilio webhook signature matches your `WEBHOOK_URL` and `TWILIO_AUTH_TOKEN`.
- If using local development, set `DEBUG=true` temporarily (signature validation is bypassed when `DEBUG=true` and no signature is present).

## 2) Netlify URL never appears
- Verify `NETLIFY_AUTH_TOKEN` is set.
- Check Celery worker logs for Netlify deploy failures.

## 3) WebSocket progress stays at `queued`
- Ensure the backend created `deployment_statuses` rows.
- Verify you are connecting to the correct request id.

## 4) Dashboard returns `401 Missing token`
- Sign in via frontend and use the JWT.
- Backend dashboard endpoints require `Authorization: Bearer <token>`.

## 5) Template output doesn’t change after editing
- Ensure your edit command includes supported intents:
  - `Reorder sections: hero, about, ...`
  - `Switch template restaurant|portfolio|store|blog|agency|saas`
  - `Make theme blue|red|green|dark|indigo|warm`
