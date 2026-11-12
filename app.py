"""
app.py — Servidor de Crecer Digital · CotizaBot (PayPal AI Hackathon).

Servidor ligero con SOLO la biblioteca estándar de Python 3: sirve la
página y los endpoints:

  GET  /              → la demo (static/index.html)
  GET  /api/health    → estado y modo de generación activo
  GET  /api/config    → client-id PÚBLICO de PayPal JS SDK (sandbox por defecto)
  POST /api/quote     → genera la cotización {headline, pitch, items, total, mode}

Modos de generación (transparentes, la UI siempre lo declara):
  - "llama-live": si LLAMA_SERVER_URL apunta a un llama-server vivo, un
    modelo local real (Qwen3 vía llama.cpp, en la máquina de la casa)
    redacta el texto comercial. Los precios salen del catálogo fijo.
  - "structured-demo": sin servidor de modelo (así corre la demo pública,
    porque un modelo de 5 GB no cabe en el hosting gratuito), redacta el
    generador estructurado de engine.py. NO se disfraza de IA.

Pago: botón oficial de PayPal Checkout (JS SDK) en ambiente SANDBOX.
PAYPAL_CLIENT_ID acepta el client-id de una app Sandbox propia creada en
developer.paypal.com; por defecto usa "sb", el client-id público de
demostración sandbox de PayPal. Ningún cargo real es posible en sandbox.

Ejecutar:   python3 app.py            → http://localhost:8000
Puerto:     variable de entorno PORT (por defecto 8000).
"""

import json
import os
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

import engine
import llm_client

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
STATIC_DIR = os.path.join(BASE_DIR, "static")


def generation_mode():
    if llm_client.is_configured() and llm_client.health_ok():
        return "llama-live"
    return "structured-demo"


def build_quote(profile):
    quote = engine.build_quote(profile)
    mode = generation_mode()
    text = None
    model_label = None
    if mode == "llama-live":
        try:
            text = llm_client.write_pitch(quote)
        except Exception:
            text = None
        if text:
            model_label = f"Qwen3 local · llama.cpp · {llm_client.model_name()}"
        else:
            mode = "structured-demo"
    if text is None:
        text = engine.structured_pitch(quote)
    return engine.public_quote(quote, text, mode, model_label)


def paypal_client_id():
    # Client-id PÚBLICO del JS SDK (no es un secreto; viaja al navegador).
    # "sb" = client-id de demostración del ambiente Sandbox de PayPal.
    return os.environ.get("PAYPAL_CLIENT_ID", "sb")


class Handler(BaseHTTPRequestHandler):
    def log_message(self, *args):
        pass

    def _send(self, code, body, content_type="application/json; charset=utf-8"):
        data = body.encode("utf-8") if isinstance(body, str) else body
        self.send_response(code)
        self.send_header("Content-Type", content_type)
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self):
        path = urlparse(self.path).path
        if path in ("/", "/index.html"):
            with open(os.path.join(STATIC_DIR, "index.html"), encoding="utf-8") as f:
                self._send(200, f.read(), "text/html; charset=utf-8")
        elif path == "/api/health":
            self._send(200, json.dumps({
                "ok": True,
                "mode": generation_mode(),
                "llama_configured": llm_client.is_configured(),
                "model": llm_client.model_name() if llm_client.is_configured() else None,
                "paypal_env": "sandbox",
            }))
        elif path == "/api/config":
            self._send(200, json.dumps({
                "paypal_client_id": paypal_client_id(),
                "paypal_env": "sandbox",
                "currency": "USD",
            }))
        else:
            self._send(404, json.dumps({"error": "not found"}))

    def do_POST(self):
        path = urlparse(self.path).path
        if path != "/api/quote":
            self._send(404, json.dumps({"error": "not found"}))
            return
        try:
            length = int(self.headers.get("Content-Length", 0))
            profile = json.loads(self.rfile.read(length) or b"{}")
        except Exception:
            self._send(400, json.dumps({"error": "invalid json"}))
            return
        try:
            self._send(200, json.dumps(build_quote(profile), ensure_ascii=False))
        except Exception as exc:
            self._send(500, json.dumps({"error": str(exc)}))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", "8000"))
    print(f"Crecer Digital · CotizaBot en http://0.0.0.0:{port} "
          f"(modo: {generation_mode()}, PayPal: sandbox)")
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()
