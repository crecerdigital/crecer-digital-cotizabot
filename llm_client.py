"""
llm_client.py — Cliente para el modelo local REAL de la casa.

Habla con un servidor llama.cpp (llama-server) por su API compatible con
OpenAI (`/v1/chat/completions`). En la operación de Crecer Digital ese
servidor corre en la máquina propia con Qwen3-8B (GGUF Q4_K_M), sin costo
por token y sin que los datos salgan de la casa.

Configuración (solo variables de entorno, nunca claves en el repo):
  LLAMA_SERVER_URL  p. ej. http://127.0.0.1:8080  (sin esto, modo inactivo)
  LLAMA_MODEL       etiqueta del modelo servido (defecto: qwen3-8b-local)

Arranque del servidor local (ver README):
  llama-server -m Qwen3-8B-Q4_K_M.gguf --port 8080 -c 4096

El modelo redacta SOLO el texto comercial (titular y pitch). Los precios
los fija engine.py desde el catálogo: si el modelo escribiera una cifra,
el servidor la descarta y usa el total del catálogo.
"""

import json
import os
import urllib.request

TIMEOUT = 300


def server_url():
    return (os.environ.get("LLAMA_SERVER_URL") or "").rstrip("/")


def is_configured():
    return bool(server_url())


def model_name():
    return os.environ.get("LLAMA_MODEL", "qwen3-8b-local")


def health_ok():
    if not is_configured():
        return False
    try:
        req = urllib.request.Request(server_url() + "/health")
        with urllib.request.urlopen(req, timeout=5) as resp:
            return resp.status == 200
    except Exception:
        return False


def write_pitch(quote):
    """Pide al modelo local el titular + pitch. Devuelve dict o None."""
    if not is_configured():
        return None
    lang = quote["lang"]
    if lang == "es":
        system = ("Eres el redactor comercial de Crecer Digital, una agencia que "
                  "ayuda a micro-negocios latinos. Escribes español claro, cálido y "
                  "directo, sin exagerar y sin inventar datos. Nunca menciones "
                  "precios ni cifras: los precios los pone el sistema.")
        user = (
            f"Negocio: {quote['business']}\n"
            f"Rubro: {quote['industry']}\n"
            f"Ciudad: {quote['city'] or 'no indicada'}\n"
            f"Servicio cotizado: {quote['service_name']}\n"
            f"Meta del cliente: {quote['goal'] or 'atraer más clientes'}\n\n"
            "Escribe EXACTAMENTE con este formato:\n"
            "TITULAR: <una línea breve>\n"
            "PITCH: <un párrafo de 70 a 110 palabras que explique el problema del "
            "cliente, qué incluye el servicio y el resultado concreto que busca>\n"
            "/no_think"
        )
    else:
        system = ("You are the copywriter for Crecer Digital, an agency that helps "
                  "Latino micro-businesses. You write clear, warm, direct English, "
                  "never exaggerating and never inventing facts. Never mention "
                  "prices or figures: the system sets the prices.")
        user = (
            f"Business: {quote['business']}\n"
            f"Industry: {quote['industry']}\n"
            f"City: {quote['city'] or 'not provided'}\n"
            f"Quoted service: {quote['service_name']}\n"
            f"Client goal: {quote['goal'] or 'attract more customers'}\n\n"
            "Write EXACTLY in this format:\n"
            "HEADLINE: <one short line>\n"
            "PITCH: <one paragraph of 70 to 110 words explaining the customer's "
            "problem, what the service includes, and the concrete outcome>\n"
            "/no_think"
        )
    payload = {
        "model": model_name(),
        "messages": [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ],
        "temperature": 0.7,
        "max_tokens": 300,
    }
    req = urllib.request.Request(
        server_url() + "/v1/chat/completions",
        data=json.dumps(payload).encode("utf-8"),
        headers={"Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(req, timeout=TIMEOUT) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        text = data["choices"][0]["message"]["content"].strip()
    except Exception:
        return None
    headline, pitch = None, None
    for line in text.splitlines():
        low = line.lower()
        if low.startswith(("titular:", "headline:")):
            headline = line.split(":", 1)[1].strip()
        elif low.startswith("pitch:"):
            pitch = line.split(":", 1)[1].strip()
    if pitch is None and text:
        pitch = text
    if not pitch:
        return None
    if lang == "es":
        validity = "Cotización válida por 7 días. Precios en USD."
        next_steps = ("Para apartar tu fecha, confirma con el pago seguro de PayPal "
                      "(ambiente Sandbox en esta demo). El trabajo arranca el mismo día "
                      "en que se confirma el encargo.")
        fallback_headline = f"Cotización para {quote['business']} — {quote['service_name']}"
    else:
        validity = "Quote valid for 7 days. Prices in USD."
        next_steps = ("To lock your date, confirm with secure PayPal checkout "
                      "(Sandbox environment in this demo). Work starts the same day "
                      "the order is confirmed.")
        fallback_headline = f"Quote for {quote['business']} — {quote['service_name']}"
    return {"headline": headline or fallback_headline, "pitch": pitch,
            "validity": validity, "next_steps": next_steps}
