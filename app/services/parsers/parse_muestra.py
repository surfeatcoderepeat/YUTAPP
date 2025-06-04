# app/services/parsers/parse_muestra.py
import openai
import json
from app.core.config import get_settings

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_muestra(mensaje: str, user: str) -> dict:
    prompt = f"""
Extraé los siguientes campos para registrar una muestra de cerveza:

- id_lote (número de lote, como 407)
- etapa (por ejemplo: fin de fermentación, pre-gelatina, pre-embarrilado)
- fecha (si no está, usar fecha de hoy)
- responsable (nombre de quien tomó la muestra)
- observaciones (estado, densidad, resultados, etc.)

Ejemplo:
"Muestra tomada del lote 407 antes de adicionar gelatina. Densidad: 1.012. Responsable: Juani."

⚠️ Devolvé solo JSON, sin comentarios, sin bloques ```json.
Mensaje:
\"\"\"{mensaje}\"\"\"
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
    