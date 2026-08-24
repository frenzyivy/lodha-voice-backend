# Lodha voice AI backend

## Run locally

```bash
python -m venv venv
source venv/bin/activate        # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env            # then edit .env with your own secrets
python seed.py                  # inserts the 5 projects — edit seed.py with real data first
uvicorn main:app --reload
```

Open http://127.0.0.1:8000/docs for interactive Swagger docs — test every endpoint from there before wiring up Vapi.

## Test the Vapi-facing endpoints

All `/vapi/*` routes require the header `x-vapi-secret: <your VAPI_SHARED_SECRET>`.

```bash
curl -X POST http://127.0.0.1:8000/vapi/functions/get-project-info \
  -H "Content-Type: application/json" \
  -H "x-vapi-secret: change-me-in-production" \
  -d '{"project_name": "Lodha Project 1"}'
```

Try a name that doesn't exist too, and confirm you get the "not one we have information on" guardrail response back — that's the response Vapi will read out to the caller.

## Test the dashboard-facing endpoints

All `/api/*` routes require the header `Authorization: Bearer <your DASHBOARD_TOKEN>`.

```bash
curl http://127.0.0.1:8000/api/stats \
  -H "Authorization: Bearer change-me-too"
```

## Before going live

1. Replace every placeholder value in `seed.py` with your real 5 projects.
2. Set real, random values for `VAPI_SHARED_SECRET` and `DASHBOARD_TOKEN` (don't ship the defaults).
3. In Vapi, register these as functions/webhook, each with the header `x-vapi-secret` set to match:
   - `POST https://<your-railway-url>/vapi/functions/get-project-info`
   - `POST https://<your-railway-url>/vapi/functions/list-projects`
   - `POST https://<your-railway-url>/vapi/functions/log-lead`
   - End-of-call webhook: `POST https://<your-railway-url>/vapi/webhook/call-ended`
4. On Railway: attach a persistent volume mounted at `/data`, set `DATABASE_URL=sqlite:////data/lodha.db`, or your data disappears on every redeploy.
5. Set `ALLOWED_ORIGINS` to your real Vercel dashboard URL once it exists.

## Note on this environment

This code was written and syntax-checked here, but this sandbox has no network access, so I couldn't `pip install` and actually run the server or make a live HTTP call against it. Run the steps above locally before deploying — if anything doesn't behave as expected, paste the error back to me and I'll fix it.
