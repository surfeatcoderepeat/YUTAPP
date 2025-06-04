# app/services/message_router.py

import openai
from app.core.config import get_settings

settings = get_settings()
openai.api_key = settings.openai_api_key

CLASES_VALIDAS = [
    "Registrar nuevo cliente",
    "Registrar nuevo producto",
    "Registrar nuevo barril",
    "Registrar nueva botella",
    "Registrar nuevo fermentador",
    "Registrar nuevo rótulo",
    "Registrar registro fermentador",
    "Registrar despacho de cerveza",
    "Registrar retorno de botellas",
    "Registrar retorno de barriles",
    "Registrar venta",
    "Registrar precio"
]

async def clasificar_mensaje(mensaje: str) -> dict:
    prompt = f"""
Actuá como un sistema automático de interpretación y clasificación de mensajes en el contexto de una cervecería artesanal. 
Tu tarea es leer un mensaje recibido y determinar qué tipo de acción corresponde realizar, eligiendo una sola opción entre las siguientes:

{chr(10).join([f"{i+1}. {opcion}" for i, opcion in enumerate(CLASES_VALIDAS)])}

Si no estás seguro, respondé únicamente con "desconocido".

Mensaje:
\"\"\"{mensaje}\"\"\"

Respondé solo con el nombre exacto de la opción correspondiente (por ejemplo, "Registrar nuevo cliente").
"""

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )

        categoria = response.choices[0].message.content.strip()

        if categoria not in CLASES_VALIDAS:
            return {
                "ok": False,
                "error": "No se pudo determinar el tipo de mensaje.",
                "categoria": "desconocido"
            }

        return {
            "ok": True,
            "categoria": categoria
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "categoria": "desconocido"
        }