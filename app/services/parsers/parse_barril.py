# app/services/parsers/parse_barril.py
import openai
import json
from app.core.config import get_settings

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_barril(mensaje: str, user: str) -> dict:
    prompt = f"""
Extraé los datos necesarios para registrar un nuevo barril a partir del siguiente mensaje.

Campos requeridos:
- id_interno (número de identificación del barril, entero)
- volumen_litros (capacidad del barril, en litros, número decimal)
- formato (debe ser siempre "barril")
- mensaje_original (el mensaje completo sin cambios)

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

        # Limpia bloques de markdown tipo ```json ... ```
        if contenido.strip().startswith("```"):
            contenido = "\n".join(
                line for line in contenido.strip().splitlines()
                if not line.strip().startswith("```")
            )

        datos = json.loads(contenido)

        faltantes = [campo for campo in ["id_interno", "volumen_litros", "formato"] if campo not in datos or not datos[campo]]

        return {
            "ok": len(faltantes) == 0,
            "faltantes": faltantes,
            "datos": datos,
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": {}
        }