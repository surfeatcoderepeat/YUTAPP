# app/services/parsers/producto.py
import openai
import json
from app.core.config import get_settings

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_producto(mensaje: str, user: str) -> dict:
    prompt = f"""
Extraé la información para registrar uno o más productos a partir del siguiente mensaje.

Por cada producto, obtené:
- nombre (str, obligatorio)
- descripción (str, opcional)

Mensaje:
\"\"\"{mensaje}\"\"\"

Devolvé una lista JSON válida con uno o más productos.
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

        productos = json.loads(contenido)

        if not isinstance(productos, list):
            raise ValueError("La respuesta no es una lista de productos.")

        faltantes = []
        for prod in productos:
            if "nombre" not in prod or not prod["nombre"]:
                faltantes.append("nombre")

        return {
            "ok": len(faltantes) == 0,
            "faltantes": faltantes,
            "datos": productos,
            "tabla_destino": "Producto"
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": {}
        }