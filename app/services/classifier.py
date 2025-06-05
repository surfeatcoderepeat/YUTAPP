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
Actuá como un sistema inteligente que interpreta mensajes en lenguaje natural dentro del contexto operativo de una cervecería artesanal. Tu tarea es clasificar el mensaje recibido y responder con una lista de las acciones que se deben registrar en la base de datos.

Estas son las únicas acciones válidas (no inventes nuevas):
{chr(10).join([f"- {opcion}" for opcion in CLASES_VALIDAS])}

⚠️ Instrucciones:
- No repitas acciones por cantidad de ítems (ej. varios barriles = una acción).
- Si el mensaje describe que se embarrila cerveza (del fermentador a barriles), devolvé:
  ["Registrar nuevo barril", "Registrar registro fermentador"]
- Si se describe un despacho de barriles a cliente, devolvé:
  ["Registrar venta", "Registrar despacho de cerveza"]
- Si no hay acciones claras, devolvé: ["desconocido"]

Ejemplo:
Mensaje: "Embarrilamos lote 33 en 5 barriles"
Respuesta: ["Registrar nuevo barril", "Registrar registro fermentador"]

Mensaje:
\"\"\"{mensaje}\"\"\"
"""

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.0,
        )
        print("[DEBUG] Respuesta bruta de OpenAI:")
        print(response.choices[0].message.content)

        categorias = response.choices[0].message.content.strip()

        # Limpiar delimitadores Markdown si están presentes
        if categorias.startswith("```"):
            categorias = categorias.split("```")[1].strip()

        try:
            categorias = json.loads(categorias)
        except:
            return {
                "ok": False,
                "error": "La respuesta no es un JSON válido.",
                "categorias": []
            }

        categorias = list(set(categorias))

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