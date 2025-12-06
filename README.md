# Trip Summary Email Service

A stateless FastAPI microservice that builds personalized trip recap emails using Supabase data, OpenRouter LLM generation, and Resend delivery.

## Features
- Retrieves trip summaries from Supabase via REST using the service role key
- Selects an email template based on persona, travel style, duration, party size, and budget
- Generates subject, preheader, text, and HTML bodies with OpenRouter-hosted models
- Sends multi-part emails through Resend
- Returns structured JSON responses for success and failure cases

## Requirements
- Python 3.11+
- Environment variables:
  - `SUPABASE_URL`
  - `SUPABASE_SERVICE_KEY`
  - `RESEND_API_KEY`
  - `OPEN_ROUTER_SK`
  - `LLM_MODEL_NAME`
  - `FRONTEND_TRIP_BASE_URL`
  - `EMAIL_FROM`
  - `ENV` (optional)

## Installation
```bash
pip install -r requirements.txt
```

## Running the service
```bash
export SUPABASE_URL=...
export SUPABASE_SERVICE_KEY=...
export RESEND_API_KEY=...
export OPEN_ROUTER_SK=...
export LLM_MODEL_NAME=...
export FRONTEND_TRIP_BASE_URL=...
export EMAIL_FROM=...
uvicorn app.main:app --host 0.0.0.0 --port 8000
```

## Endpoint
`POST /send-trip-summary-email`

### Request body
```json
{
  "summary_id": "<trip_summary_uuid>"
}
```

### Successful response
```json
{
  "ok": true,
  "email_id": "<resend_message_id>",
  "summary_id": "<trip_summary_uuid>"
}
```

### Functional error response
```json
{
  "ok": false,
  "error": "SUMMARY_NOT_FOUND",
  "detail": "Trip summary not found"
}
```

### Technical error response
```json
{
  "ok": false,
  "error": "INTERNAL_ERROR",
  "detail": "<details>"
}
```

## Docker
```bash
docker build -t trip-email-service .
docker run -e SUPABASE_URL=... -e SUPABASE_SERVICE_KEY=... -e RESEND_API_KEY=... -e OPEN_ROUTER_SK=... -e LLM_MODEL_NAME=... -e FRONTEND_TRIP_BASE_URL=... -e EMAIL_FROM=... -p 8000:8000 trip-email-service
```
