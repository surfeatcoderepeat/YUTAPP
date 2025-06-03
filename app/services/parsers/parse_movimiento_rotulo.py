# app/services/parsers/parse_movimiento_rotulo.py
import openai
import json
from app.core.config import get_settings

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_movimiento_rotulo(mensaje: str, user: str) -> dict:
    prompt = f"""
Extraé los datos necesarios para registrar un movimiento de rótulos.

Campos requeridos:
- tipo (entrada o salida)
- cantidad (cantidad de rótulos, número entero)
- producto (producto al que corresponden los rótulos, ej: 'IPA', 'Cream Ale', etc.)
- responsable (usuario que lo envía: '{user}')
- observacion (si hay, opcional)
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

        campos_obligatorios = ["tipo", "cantidad", "producto", "responsable", "mensaje_original"]
        faltantes = [campo for campo in campos_obligatorios if campo not in datos or not datos[campo]]

        return {
            "ok": len(faltantes) == 0,
            "faltantes": faltantes,
            "datos": datos,
            "tabla_destino": "MovimientoRotulo"
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": {}
        }