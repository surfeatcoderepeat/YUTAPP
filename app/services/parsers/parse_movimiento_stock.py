# app/services/parsers/parse_movimiento_stock.py
import openai
import json
from app.core.config import get_settings

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_movimiento_stock(mensaje: str, user: str) -> dict:
    prompt = f"""
Extraé los datos necesarios para registrar un movimiento de stock de cerveza artesanal.

Campos requeridos:
- tipo (ej: "salida" o "entrada")
- producto (ej: "IPA", "APA", etc.)
- formato (ej: "barril", "botella")
- volumen_litros (número decimal, litros)
- lote (entero)
- cliente (nombre del cliente)
- responsable (siempre: "{user}")
- id_barril (si el formato es "barril", número entero)
- observacion (si hubiera, opcional)
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

        campos_obligatorios = ["tipo", "producto", "formato", "volumen_litros", "lote", "cliente", "responsable", "mensaje_original"]
        faltantes = [campo for campo in campos_obligatorios if campo not in datos or not datos[campo]]

        if datos.get("formato", "").lower() == "barril" and not datos.get("id_barril"):
            faltantes.append("id_barril")

        return {
            "ok": len(faltantes) == 0,
            "faltantes": faltantes,
            "datos": datos,
            "tabla_destino": "MovimientoStock"
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": {}
        }