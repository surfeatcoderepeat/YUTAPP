# app/interfaces/parsers/producto.py
import json
from app.infrastructure.config import get_settings
from app.infrastructure.repositories.producto_repo import ProductoRepository
from app.services.llm.openai_client import OpenAIClient

settings = get_settings()

async def parse_producto(mensaje: str, user: str) -> dict:
    client = OpenAIClient()
    prompt = f"""
Extraé el nombre y la descripción (opcional) de un producto a partir del siguiente mensaje.

Mensaje:
\"\"\"{mensaje}\"\"\"

Devolvé un único objeto JSON con dos claves: "nombre" (str, obligatorio) y "descripcion" (str, opcional).
"""

    try:
        response = await client.extract_json(prompt)
        if not response or not response.choices:
            raise ValueError("No se recibió una respuesta válida del cliente LLM.")
        contenido = response.choices[0].message.content

        if contenido.strip().startswith("```"):
            contenido = "\n".join(
                line for line in contenido.strip().splitlines()
                if not line.strip().startswith("```")
            )

        producto = json.loads(contenido)

        nombre = producto.get("nombre", "").strip()
        if not nombre:
            return {"ok": False, "error": "El producto no tiene nombre."}

        if ProductoRepository().exists(nombre):
            return {"ok": False, "error": f"El producto '{nombre}' ya existe."}

        return {
            "ok": True,
            "datos": {
                "nombre": nombre,
                "descripcion": producto.get("descripcion", "")
            },
            "tabla_destino": "Producto"
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": {}
        }