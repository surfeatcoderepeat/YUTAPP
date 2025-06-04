# app/services/parsers/parse_venta.py
import openai
import json
from app.core.config import get_settings

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_venta(mensaje: str, user: str) -> dict:
    prompt = f"""
Extraé los siguientes datos de una venta:

- producto (nombre del estilo)
- formato (botella o barril)
- volumen_litros (por unidad)
- cantidad (número de unidades)
- fecha_pedido (si no se menciona, usar fecha de hoy)
- fecha_cobro (si no se menciona, dejar nulo)
- responsable (nombre de quien registró la venta)
- cliente (nombre del cliente)

Devolvé solo un JSON válido. No uses markdown ni comentarios.

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