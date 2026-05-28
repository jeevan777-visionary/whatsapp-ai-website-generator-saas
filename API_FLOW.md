# API Flow

1. `POST /webhook/whatsapp` receives Twilio form payload.
2. Payload is validated, rate-limited, and queued.
3. Worker extracts website requirements with Groq.
4. Worker generates copy, renders files, zips artifacts.
5. Netlify deployment returns production URL.
6. WhatsApp status messages are sent:
   - Generating
   - Deploying
   - Live URL or failure notice
