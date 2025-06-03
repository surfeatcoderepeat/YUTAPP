# app/services/parsers/parse_muestra.py
import openai
import json
from app.core.config import get_settings

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_muestra(mensaje: str, user: str) -> dict:
    prompt = f"""
Extraé los datos necesarios para registrar una muestra tomada de un lote en fermentación.

Campos requeridos:
- lote (número del lote)
- fermentador (número del fermentador asociado)
- momento (etapa en la que se tomó la muestra: ej. "antes de adicionar gelatina", "final de fermentación", etc.)
- densidad (si se menciona, opcional, como número flotante)
- estado (texto descriptivo corto)
- responsable (usuario que lo envía: '{user}')
- mensaje_original (mensaje completo sin cambios)

Mensaje:
\"\"\"{mensaje}\"\"\"

Devolvé solo un JSON válido, sin explicaciones ni comentarios.
"""

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        contenido = response.choices[0].message.content

        if contenido.strip().startswith("```"):
            contenido = "\n".join(
                line for line in contenido.strip().splitlines()
                if not line.strip().startswith("```")
            )

        datos = json.loads(contenido)

        campos_obligatorios = ["lote", "fermentador", "momento", "estado", "responsable", "mensaje_original"]
        faltantes = [campo for campo in campos_obligatorios if campo not in datos or not datos[campo]]

        return {
            "ok": len(faltantes) == 0,
            "faltantes": faltantes,
            "datos": datos,
            "tabla_destino": "Muestra"
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": {}
        }
    