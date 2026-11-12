# Devpost — PayPal AI Hackathon · Textos completos del envío
# Proyecto: «Crecer Digital» (submission 1264098) — preparado 2026-11-11
# Regla de la casa: la página es la última milla. Todo se pega DESDE este archivo.
#
# ⚠️ ANTES DE PEGAR, verificar/reemplazar si el nombre asignado difiere:
#   DEMO_URL  = https://crecer-digital-cotizabot.onrender.com
#   REPO_URL  = https://github.com/crecerdigital/crecer-digital-cotizabot
#   VIDEO_URL = __PEGAR_TRAS_SUBIDA__ (URL pública de YouTube del video demo <3 min)
#
# Pasos ya completos en el borrador (2/5): Manage team ✔ · Project overview ✔
# Pendientes: Project details (abajo), Additional info (abajo), Submit.

=====================================================================
PROJECT DETAILS
=====================================================================

## Project name (ya está en el borrador, no cambiar)
Crecer Digital

## Tagline / Elevator pitch (si el campo lo pide)
CotizaBot by Crecer Digital: a local-AI quoting assistant that turns a Latino micro-business's story into a priced, ready-to-pay quote in one minute — with PayPal Checkout built in.

## Inspiration
Crecer Digital is a real one-person content agency serving Latino micro-businesses — taquerías, beauty salons, cleaning crews, event halls — whose owners run everything from their phones. The slowest, leakiest step in their sales is the quote: a WhatsApp thread that goes cold, a price invented on the spot, a follow-up that never happens. We built the tool we needed ourselves: an assistant that writes the quote like we would, prices it from our real catalog, and closes with a PayPal button — while the AI runs on our own hardware, because a one-person agency cannot pay per-token rent and our clients' data should never leave the house.

## What it does
CotizaBot takes a 30-second intake (business name, industry, city, the service they want, and their goal) and produces a complete sales quote: a headline and pitch written for that specific business, the service's deliverables, an itemized price table with our real catalog prices, an automatic 10% bundle discount when the industry-matched add-on applies, and a total — followed immediately by an official PayPal Checkout button (Sandbox) for the exact quoted amount. Approving the sandbox payment shows the order confirmation, exactly as a real client confirmation would. The interface is Spanish-first with an English toggle, because our clients are.

## How we built it
The whole server is Python 3 standard library only — no frameworks, no pip installs — serving a single-page UI, a quote API, and a config endpoint. Quote generation has two honestly-labeled modes (the UI always shows which one is active): (1) llama-live — a real local model, Qwen3 (GGUF Q4_K_M) served by llama.cpp on the agency's own machine through its OpenAI-compatible API, writes the headline and pitch; prices never come from the model, only from the fixed catalog in code. (2) structured-demo — a transparent deterministic generator (per-industry templates + catalog logic) used by the public deployment, because a 5 GB model does not fit free hosting; the demo declares this mode in a visible badge instead of dressing templates up as AI. Payments use the official PayPal JS SDK in the Sandbox environment, with the quoted total passed to createOrder and an onApprove capture that renders the sandbox order ID as the confirmation.

## Challenges we ran into
Fitting a real LLM into a zero-budget, honest demo was the core challenge: an 8B model will not run on free hosting, and we refuse to fake AI with templates. The answer was architectural honesty — one codebase, two declared modes, and a health endpoint that reports which mode is live, so judges can run the real model locally with three commands. CPU inference on our small server is slow (1–3 minutes per quote), which forced careful prompt design: a strict output format, no-think mode, and a hard rule that the model writes words, never numbers.

## Accomplishments that we're proud of
A complete, working sales loop — intake → AI-written quote → itemized real prices → PayPal Sandbox checkout → order confirmation — built with zero dependencies and zero budget, in Spanish and English, by the same one-person operation that will actually use it with real clients the week after the hackathon.

## What we learned
That honesty is a feature users can feel: the mode badge made us design the fallback as a real product instead of a trick. And that owning a small local model changes the economics of AI for a micro-agency — no per-token bill, no client data leaving the house, and a tool that keeps working even when a subscription doesn't.

## What's next for Crecer Digital
Connect CotizaBot to the agency's real PayPal account and catalog so the first client quotes go out the week after judging; add WhatsApp delivery of the quote link (how our clients actually buy); and keep improving the local model's copy with the agency's real quote history — on our server, under our roof.

## Built with
python · llama.cpp · qwen3 · paypal-checkout-js-sdk · render · javascript · html · css

## "Try it out" links
- Live demo: https://crecer-digital-cotizabot.onrender.com
- Code (MIT): https://github.com/crecerdigital/crecer-digital-cotizabot
- Video: __PEGAR_TRAS_SUBIDA__

=====================================================================
ADDITIONAL INFO
=====================================================================

## Project start date
Registered on Devpost October 25, 2026. Working prototype built November 11, 2026.

## Demo URL
https://crecer-digital-cotizabot.onrender.com

## Repository URL (public, MIT license visible)
https://github.com/crecerdigital/crecer-digital-cotizabot

## Video URL (public YouTube, under 3 minutes)
__PEGAR_TRAS_SUBIDA__

## How judges can test it (instructions)
1. Open the live demo and fill the form — sample: Business "Taquería Doña Mary", Industry "Comida y restaurante", City "Charlotte, NC", Service "Paquete mensual de contenido", Goal "llenar los fines de semana". Click "Generar mi cotización".
2. You will see the quote with its itemized prices and the PayPal Sandbox button. The badge at the top declares the public demo's generation mode (structured generator — see the transparency note below).
3. To complete the sandbox checkout, sign in at the PayPal window with a Sandbox test buyer account from your own PayPal developer dashboard (developer.paypal.com → Sandbox → Accounts gives you pre-made test accounts; the demo's PayPal client-id is the public sandbox demo id "sb", or set PAYPAL_CLIENT_ID to your own sandbox app's client-id when self-hosting). Sandbox uses test money only — no real charge is possible.
4. To run the REAL local AI (Qwen3-8B via llama.cpp), clone the repo and follow the README: start llama-server with a Qwen3 GGUF (8B or 4B), then run LLAMA_SERVER_URL=http://127.0.0.1:8080 python3 app.py — GET /api/health will report "mode": "llama-live" and the UI badge turns green. No API keys or paid services are needed at any point.

## Transparency note (also in the README)
The public demo runs in "structured-demo" mode and says so in the UI: a 5 GB local model cannot run on free hosting, so the hosted copy uses our deterministic quote generator while the identical codebase runs the real Qwen3 model on our own server (8B there; this build was verified end-to-end with the 4B on a small shared-CPU machine). We chose a declared fallback over a disguised one.
