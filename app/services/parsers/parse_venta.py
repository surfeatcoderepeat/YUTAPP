# app/services/parsers/parse_venta.py
import openai
import json
from app.core.config import get_settings

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_venta(mensaje: str, user: str) -> dict:
    prompt = f"""
Extraé los datos necesarios para registrar una venta de cerveza artesanal.

Campos requeridos:
- producto (ej: "IPA", "APA", etc.)
- formato (ej: "botella", "barril")
- volumen_litros (cantidad total vendida en litros)
- cliente (nombre del cliente)
- fecha_pedido (fecha de la venta o del pedido, en formato YYYY-MM-DD)
- fecha_cobro (fecha de cobro si se menciona, en formato YYYY-MM-DD, puede ser null)
- responsable (usuario que lo envía: "{user}")
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

        campos_obligatorios = ["producto", "formato", "volumen_litros", "cliente", "fecha_pedido", "responsable", "mensaje_original"]
        faltantes = [campo for campo in campos_obligatorios if campo not in datos or not datos[campo]]

        return {
            "ok": len(faltantes) == 0,
            "faltantes": faltantes,
            "datos": datos,
            "tabla_destino": "Venta"
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": {}
        }