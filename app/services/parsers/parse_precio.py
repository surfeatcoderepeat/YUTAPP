# app/services/parsers/parse_precio.py
import openai
import json
from app.core.config import get_settings

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_precio(mensaje: str, user: str) -> dict:
    prompt = f"""
Extraé los datos para registrar un precio por litro de un producto según el siguiente mensaje.

Campos requeridos:
- producto (por ejemplo: APA, IPA, cualquier estilo)
- formato (por ejemplo: botella o barril)
- precio_litro (valor numérico en reales)
- mensaje_original (el mensaje original completo)

Ejemplo de mensaje:
"El precio por litro en botella de cualquier estilo es 25 reales."

Mensaje:
\"\"\"{mensaje}\"\"\"

Devolvé solo un JSON válido, sin explicaciones ni comentarios.
"""

    try:
        print("[DEBUG] Enviando prompt a OpenAI:", prompt)
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        contenido = response.choices[0].message.content
        print("[DEBUG] Respuesta de OpenAI:", contenido)

        # Limpia bloques de markdown tipo ```json ... ```
        if contenido.strip().startswith("```"):
            contenido = "\n".join(
                line for line in contenido.strip().splitlines()
                if not line.strip().startswith("```")
            )
            print("[DEBUG] Contenido limpio:", contenido)

        datos = json.loads(contenido)
        print("[DEBUG] JSON parseado:", datos)

        campos_obligatorios = ["producto", "formato", "precio_litro"]
        faltantes = [campo for campo in campos_obligatorios if campo not in datos or not datos[campo]]

        datos["mensaje_original"] = mensaje

        return {
            "ok": len(faltantes) == 0,
            "faltantes": faltantes,
            "datos": datos,
            "tabla_destino": "Precio"
        }

    except Exception as e:
        print("[ERROR] Excepción durante el parseo:", e)
        return {
            "ok": False,
            "error": str(e),
            "datos": {}
        }