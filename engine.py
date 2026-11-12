"""
engine.py — Motor de cotizaciones de Crecer Digital (CotizaBot).

Dos modos de generación, SIEMPRE declarados en la respuesta y en la UI:

  - "llama-live": un modelo local real (Qwen3-8B vía llama.cpp, ver
    llm_client.py) redacta la descripción del servicio. Los PRECIOS nunca
    los inventa el modelo: salen del catálogo fijo de abajo y el total lo
    calcula este módulo.

  - "structured-demo": generador estructurado y determinista de esta casa
    (plantillas por industria/tono + lógica de catálogo). Es el modo de la
    demo pública porque un modelo de 5 GB no cabe en el hosting gratuito.
    NO se disfraza de IA: la UI y el README lo dicen tal cual.

Catálogo real de servicios de Crecer Digital (precios en USD, los mismos
que la agencia ofrece a micro-negocios latinos).
"""

SERVICES = {
    "contenido-mensual": {
        "es": "Paquete mensual de contenido para redes (12 piezas)",
        "en": "Monthly social media content package (12 pieces)",
        "price": 149,
        "deliverables_es": [
            "12 piezas de contenido (video corto, imagen o carrusel)",
            "Textos y hashtags en español e inglés",
            "Calendario de publicación del mes",
            "1 ronda de ajustes por pieza",
        ],
        "deliverables_en": [
            "12 content pieces (short video, image or carousel)",
            "Captions and hashtags in Spanish and English",
            "Monthly posting calendar",
            "1 revision round per piece",
        ],
    },
    "reel": {
        "es": "Video corto vertical (Reel / TikTok / Shorts)",
        "en": "Short vertical video (Reel / TikTok / Shorts)",
        "price": 49,
        "deliverables_es": [
            "1 video vertical de 30–45 segundos",
            "Guion y textos en pantalla que sí caben",
            "Subtítulos incluidos",
            "Portada y texto de publicación",
        ],
        "deliverables_en": [
            "1 vertical video, 30–45 seconds",
            "Script and on-screen text that actually fits",
            "Captions included",
            "Cover and posting copy",
        ],
    },
    "diseno": {
        "es": "Diseño de menú, flyer o catálogo digital",
        "en": "Menu, flyer or digital catalog design",
        "price": 39,
        "deliverables_es": [
            "1 pieza de diseño lista para imprimir y para WhatsApp",
            "Versión en español e inglés",
            "Archivos PNG y PDF",
            "1 ronda de ajustes",
        ],
        "deliverables_en": [
            "1 design piece, print-ready and WhatsApp-ready",
            "Spanish and English versions",
            "PNG and PDF files",
            "1 revision round",
        ],
    },
    "web": {
        "es": "Página web sencilla de una sección",
        "en": "Simple one-section website",
        "price": 199,
        "deliverables_es": [
            "Página de una sección con servicios, fotos y contacto",
            "Botón directo a WhatsApp",
            "Diseño que se ve bien en el teléfono",
            "Texto en español e inglés",
        ],
        "deliverables_en": [
            "One-section page with services, photos and contact",
            "Direct WhatsApp button",
            "Mobile-first design",
            "Copy in Spanish and English",
        ],
    },
    "fotos": {
        "es": "Sesión de fotos de producto (dirección remota)",
        "en": "Product photo session (remote direction)",
        "price": 89,
        "deliverables_es": [
            "Dirección de la sesión paso a paso por videollamada",
            "20 fotos editadas y listas para redes",
            "Guía de luz y fondo con lo que ya tienes",
            "Versiones cuadrada y vertical",
        ],
        "deliverables_en": [
            "Step-by-step session direction over video call",
            "20 edited photos, social-ready",
            "Lighting and backdrop guide with what you already own",
            "Square and vertical versions",
        ],
    },
}

INDUSTRIES = {
    "comida": {
        "es": "comida y restaurante",
        "en": "food and restaurant",
        "pain_es": "tus clientes deciden por lo que ven en el teléfono antes de llegar",
        "pain_en": "your customers decide from what they see on their phone before they ever walk in",
        "hook_es": "que cada plato se vea tan bien como sabe",
        "hook_en": "making every dish look as good as it tastes",
    },
    "belleza": {
        "es": "belleza y cuidado personal",
        "en": "beauty and personal care",
        "pain_es": "las clientas nuevas llegan por Instagram y por recomendación, en ese orden",
        "pain_en": "new clients arrive through Instagram and word of mouth, in that order",
        "hook_es": "que tu trabajo se vea profesional antes de la primera cita",
        "hook_en": "making your work look professional before the first appointment",
    },
    "limpieza": {
        "es": "limpieza y servicios del hogar",
        "en": "cleaning and home services",
        "pain_es": "la confianza se gana con fotos reales del antes y el después",
        "pain_en": "trust is earned with real before-and-after photos",
        "hook_es": "mostrar resultados reales que consiguen llamadas",
        "hook_en": "showing real results that turn into calls",
    },
    "reparaciones": {
        "es": "reparaciones y oficios",
        "en": "repairs and trades",
        "pain_es": "quien busca un técnico en Google llama al que se ve más serio",
        "pain_en": "whoever searches for a technician on Google calls the one who looks most serious",
        "hook_es": "que tu oficio se vea tan confiable como tu trabajo",
        "hook_en": "making your trade look as reliable as your work",
    },
    "eventos": {
        "es": "eventos y celebraciones",
        "en": "events and celebrations",
        "pain_es": "las familias comparan salones y servicios desde el teléfono y deciden en minutos",
        "pain_en": "families compare venues and vendors from their phone and decide in minutes",
        "hook_es": "que tu salón o servicio sea el que se comparte en el grupo familiar",
        "hook_en": "making your venue the one shared in the family group chat",
    },
    "tienda": {
        "es": "tienda y ventas",
        "en": "retail and sales",
        "pain_es": "cada producto sin foto buena es una venta que se va a la competencia",
        "pain_en": "every product without a good photo is a sale that goes to a competitor",
        "hook_es": "que tu mercancía se venda sola desde el catálogo",
        "hook_en": "making your products sell themselves from the catalog",
    },
    "otro": {
        "es": "servicios",
        "en": "services",
        "pain_es": "tus próximos clientes están mirando su teléfono ahora mismo",
        "pain_en": "your next customers are looking at their phones right now",
        "hook_es": "que tu negocio se vea tan bueno como es",
        "hook_en": "making your business look as good as it actually is",
    },
}

# Complementos sugeridos según la industria (precio fijo de catálogo).
ADDONS = {
    "comida": ("diseno",),
    "belleza": ("reel",),
    "limpieza": ("fotos",),
    "reparaciones": ("web",),
    "eventos": ("fotos",),
    "tienda": ("fotos",),
    "otro": ("reel",),
}

BUNDLE_DISCOUNT = 0.10  # 10% si acepta el complemento sugerido en el mismo encargo.


def build_quote(profile):
    """Arma la cotización: precios y estructura siempre desde el catálogo."""
    lang = "en" if profile.get("lang") == "en" else "es"
    business = (profile.get("business") or "").strip() or (
        "Tu negocio" if lang == "es" else "Your business")
    industry_key = profile.get("industry") if profile.get("industry") in INDUSTRIES else "otro"
    service_key = profile.get("service") if profile.get("service") in SERVICES else "contenido-mensual"
    city = (profile.get("city") or "").strip()
    goal = (profile.get("goal") or "").strip()

    service = SERVICES[service_key]
    industry = INDUSTRIES[industry_key]
    items = [{
        "name": service[lang],
        "price": service["price"],
    }]
    addon_keys = [k for k in ADDONS.get(industry_key, ()) if k != service_key]
    subtotal = service["price"]
    discount = 0
    for key in addon_keys:
        addon = SERVICES[key]
        items.append({"name": addon[lang], "price": addon["price"]})
        subtotal += addon["price"]
    if addon_keys:
        discount = round(subtotal * BUNDLE_DISCOUNT)
    total = subtotal - discount

    return {
        "business": business,
        "industry": industry[lang],
        "industry_key": industry_key,
        "city": city,
        "goal": goal,
        "service_key": service_key,
        "service_name": service[lang],
        "deliverables": service["deliverables_es" if lang == "es" else "deliverables_en"],
        "items": items,
        "subtotal": subtotal,
        "discount": discount,
        "total": total,
        "currency": "USD",
        "lang": lang,
        "_industry": industry,
    }


def structured_pitch(quote):
    """Redacción determinista (modo structured-demo). No es un modelo de IA
    y nunca se presenta como tal: son plantillas de la casa por industria."""
    lang = quote["lang"]
    ind = quote["_industry"]
    business = quote["business"]
    city = quote["city"]
    goal = quote["goal"]
    if lang == "es":
        place = f" en {city}" if city else ""
        goal_line = f" Tu meta declarada: {goal}." if goal else ""
        pitch = (
            f"{business} trabaja en {quote['industry']}{place}, y la verdad es simple: "
            f"{ind['pain_es']}. Esta cotización de Crecer Digital propone "
            f"{quote['service_name'].lower()} para lograr una cosa concreta: "
            f"{ind['hook_es']}.{goal_line} "
            f"Todo el trabajo es remoto, con entrega digital y textos en español e inglés, "
            f"pensado para negocios que se manejan desde el teléfono."
        )
        headline = f"Cotización para {business} — {quote['service_name']}"
        validity = "Cotización válida por 7 días. Precios en USD."
        next_steps = ("Para apartar tu fecha, confirma con el pago seguro de PayPal "
                      "(ambiente Sandbox en esta demo). El trabajo arranca el mismo día "
                      "en que se confirma el encargo.")
    else:
        place = f" in {city}" if city else ""
        goal_line = f" Your stated goal: {goal}." if goal else ""
        pitch = (
            f"{business} works in {quote['industry']}{place}, and the truth is simple: "
            f"{ind['pain_en']}. This quote from Crecer Digital proposes "
            f"{quote['service_name'].lower()} to achieve one concrete thing: "
            f"{ind['hook_en']}.{goal_line} "
            f"All work is remote, delivered digitally, with copy in Spanish and English, "
            f"built for businesses run from a phone."
        )
        headline = f"Quote for {business} — {quote['service_name']}"
        validity = "Quote valid for 7 days. Prices in USD."
        next_steps = ("To lock your date, confirm with secure PayPal checkout "
                      "(Sandbox environment in this demo). Work starts the same day "
                      "the order is confirmed.")
    return {"headline": headline, "pitch": pitch,
            "validity": validity, "next_steps": next_steps}


def public_quote(quote, text, mode, model_label=None):
    """Respuesta final de la API (sin campos internos)."""
    out = {k: v for k, v in quote.items() if not k.startswith("_")}
    out.update(text)
    out["mode"] = mode
    out["model"] = model_label
    return out
