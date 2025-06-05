# app/services/message_router.py

import openai
import json
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
Actuá como un sistema inteligente de interpretación de mensajes en el contexto operativo de una cervecería artesanal.

Tu tarea es leer un mensaje recibido por un bot en lenguaje natural y responder con una lista de todas las acciones que se deberían registrar en la base de datos, de acuerdo a lo que el mensaje describe.

Estas son las acciones válidas que podés detectar (no inventes nuevas):

{chr(10).join([f"- {opcion}" for opcion in CLASES_VALIDAS])}

Respondé únicamente con un array JSON. Por ejemplo:
["Registrar nuevo barril", "Registrar registro fermentador"]

Si no se identifica ninguna acción clara, respondé:
["desconocido"]

Mensaje:
\"\"\"{mensaje}\"\"\"
"""

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )

        categorias = response.choices[0].message.content.strip()
        try:
            categorias = json.loads(categorias)
        except:
            return {
                "ok": False,
                "error": "La respuesta no es un JSON válido.",
                "categorias": []
            }

        categorias_validas = [c for c in categorias if c in CLASES_VALIDAS]
        if not categorias_validas:
            return {
                "ok": False,
                "error": "No se reconocieron acciones válidas.",
                "categorias": []
            }

        return {
            "ok": True,
            "categorias": categorias_validas
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "categorias": []
        }