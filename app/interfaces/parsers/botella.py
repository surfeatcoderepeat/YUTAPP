from app.infrastructure.openai.client import openai_client

async def parse_botella(mensaje: str, user: str) -> dict:
    prompt = f"""
Extraé los datos para registrar una botella a partir del siguiente mensaje.

Los campos requeridos son:
- identificador_botella (un número entero único)
- capacidad_litros (volumen en litros, como 0.33, 0.6, etc.)
- estado (vacía, limpia, sucia, etc.)
- ubicacion (como "stock fábrica")

Mensaje:
\"\"\"{mensaje}\"\"\"

Devolvé un único objeto JSON con esos campos. No incluyas explicaciones, solo el JSON.
"""

    try:
        datos = await openai_client(prompt)

        campos_requeridos = ["identificador_botella", "capacidad_litros", "estado", "ubicacion"]
        faltantes = [campo for campo in campos_requeridos if campo not in datos or datos[campo] is None]

        return {
            "ok": len(faltantes) == 0,
            "faltantes": faltantes,
            "datos": [datos],
            "tabla_destino": "Botella"
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": []
        }
