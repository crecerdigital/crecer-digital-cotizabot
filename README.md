# Crecer Digital · CotizaBot — AI quotes with PayPal checkout for Latino micro-businesses

**CotizaBot** is the quoting assistant of **Crecer Digital**, a real content
agency that serves Latino micro-businesses (taquerías, salons, cleaning
crews, event halls) run by owners who live on their phones. A business owner
describes their business; CotizaBot builds a complete, priced quote for a
content/design service in about a minute — and closes with a **PayPal
Checkout button** so the owner can confirm the order on the spot.

**Live demo:** https://crecer-digital-cotizabot.onrender.com
**Repo:** https://github.com/crecerdigital/crecer-digital-cotizabot

Built for the **PayPal AI Hackathon** (Devpost). By Crecer Digital.
MIT licensed.

## What it does

1. **Intake** — business name, industry, city, the service they want, and
   their goal (one short form, Spanish first, English toggle).
2. **Quote generation** — a headline and a sales pitch written for that
   specific business, plus deliverables, an itemized price table, a bundle
   discount when the suggested add-on applies, and a total. Prices always
   come from the agency's fixed catalog in `engine.py` — never invented.
3. **Payment** — the official **PayPal Checkout (JS SDK)** button, in the
   **Sandbox** environment, charges exactly the quoted total. On approval
   the demo shows the sandbox order confirmation.

## Honest by design: two generation modes, always declared

The UI shows a badge with the active mode at all times. Nothing is faked.

| Mode | When | What happens |
|---|---|---|
| `llama-live` | `LLAMA_SERVER_URL` points to a running llama.cpp server | A **real local model — Qwen3 (GGUF Q4_K_M) served by llama.cpp** on the agency's own machine writes the headline and pitch (`llm_client.py`). The agency server runs Qwen3-8B; this build was verified end-to-end with Qwen3-4B on a small shared-CPU machine (same family, same pipeline). Prices still come from the fixed catalog; the model never sets prices. 
| `structured-demo` | No model server (how the public demo runs) | A transparent, deterministic **structured generator** (`engine.py`: per-industry templates + catalog logic) writes the copy. A 5 GB model does not fit free hosting, so the public demo declares this mode in the UI instead of pretending to be an LLM. |

To see the real model work, run the project locally with llama.cpp as
described below — the same code path the agency runs on its own server.

## Run it locally

Requires only **Python 3.10+** — no pip installs, no frameworks
(standard library only).

```bash
python3 app.py
# → http://localhost:8000   (structured-demo mode)
```

Health check: `GET /api/health` · Quote endpoint: `POST /api/quote` (JSON).

```bash
curl -s -X POST localhost:8000/api/quote -H 'Content-Type: application/json' \
  -d '{"business":"Taquería Doña Mary","industry":"comida","city":"Charlotte, NC","service":"contenido-mensual","goal":"llenar los fines de semana","lang":"es"}'
```

### Enable the real local AI (Qwen3 via llama.cpp)

1. Get [llama.cpp](https://github.com/ggml-org/llama.cpp) and a Qwen3
   GGUF (Q4_K_M), then start the server:

   ```bash
   llama-server -m Qwen3-8B-Q4_K_M.gguf --port 8080 -c 2048 --alias qwen3-8b-local   # the 4B GGUF works too on smaller machines
   ```

2. Start CotizaBot pointing at it:

   ```bash
   LLAMA_SERVER_URL=http://127.0.0.1:8080 python3 app.py
   ```

   The health endpoint now reports `"mode": "llama-live"` and the UI badge
   turns green. Local inference is slower on CPU (expect 1–3 minutes per
   quote on a small machine) — that is the honest trade-off of owning the
   model instead of renting an API.

### PayPal Sandbox configuration

The demo works out of the box with PayPal's public sandbox demo client-id
(`PAYPAL_CLIENT_ID` defaults to `sb`), so the official PayPal buttons
render and the full sandbox checkout flow runs — **test money only, no
real charge is possible**.

To run it against **your own** PayPal Sandbox app:

1. Go to [developer.paypal.com](https://developer.paypal.com) → Log in →
   **Apps & Credentials** → Sandbox → **Create App**.
2. Copy that app's **Client ID** and start the server with it:

   ```bash
   PAYPAL_CLIENT_ID=<your-sandbox-client-id> python3 app.py
   ```

3. To complete a test purchase, use a **Sandbox test buyer account**:
   in the same PayPal developer dashboard → **Sandbox → Accounts** you
   will find pre-made test accounts (a Business and a Personal one) tied
   to your developer login, and you can create more. Use the Personal
   test account's email/password at the PayPal checkout window. These
   credentials are personal to each developer account — that is why this
   repo ships none: create yours in your own dashboard, it takes a minute.

⚠️ Never commit real credentials. Client IDs for the JS SDK are public
identifiers, but your secret keys are not used by this project at all and
must never be added to it.

## Deploy (Render)

Same pattern as the agency's other demos: create a Web Service from this
repo with **Build Command** empty and **Start Command** `python3 app.py`
(Render sets `PORT`). Optional env vars: `LLAMA_SERVER_URL`,
`PAYPAL_CLIENT_ID`. The free tier runs in `structured-demo` mode and
declares it.

## Project structure

```
app.py          HTTP server (stdlib only): page, /api/health, /api/config, /api/quote
engine.py       Service catalog with fixed prices + the structured generator
llm_client.py   Client for the local llama.cpp server (OpenAI-compatible API)
static/         Single-page UI (ES/EN), PayPal JS SDK integration
Procfile        web: python3 app.py
```

## Why it matters

Latino micro-businesses lose customers every day because quoting is slow:
a WhatsApp thread, a forgotten follow-up, a price given from memory.
CotizaBot turns that into one minute and one tap — a written quote with a
real price and a PayPal button — while the AI runs on the agency's own
hardware, so client data never leaves the house and there is no per-token
bill. That is the agency's whole model: own the tools, serve the barrio.

## License

MIT — see [LICENSE](LICENSE). Copyright (c) 2026 Cristhiam Acuña — Crecer Digital.
