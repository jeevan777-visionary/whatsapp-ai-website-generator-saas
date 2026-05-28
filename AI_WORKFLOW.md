# AI Workflow

## Extraction
- Input: natural language WhatsApp message.
- Model: Groq-hosted Llama 3 chat completion.
- Output: strict JSON requirements schema.
- Validator normalizes fields and supported website types.

## Content Generation
- Prompt requests realistic premium marketing copy.
- Output includes hero, about, services, FAQs, CTA, footer.
- Fallback content engine ensures no-block generation.

## Safety
- Input text is sanitized.
- No secrets are logged.
- Request timeouts prevent queue stalls.
