# app/services/parsers/producto.py
import openai
import json
from app.core.config import get_settings
from app.utils.productos import get_producto_id

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
        nuevos_productos = []
        duplicados = []

        for prod in productos:
            nombre = prod.get("nombre", "").strip()
            if not nombre:
                faltantes.append("nombre")
                continue

            if get_producto_id(nombre):
                duplicados.append(nombre)
                continue

            nuevos_productos.append(prod)

        return {
            "ok": len(faltantes) == 0 and len(nuevos_productos) > 0,
            "faltantes": faltantes,
            "datos": nuevos_productos,
            "tabla_destino": "Producto",
            "mensaje_info": f"Se ignoraron productos duplicados: {', '.join(duplicados)}" if duplicados else ""
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": {}
        }