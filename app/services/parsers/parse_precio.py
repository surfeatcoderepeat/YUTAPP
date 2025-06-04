# app/services/parsers/parse_precio.py
import openai
import json
from app.core.config import get_settings

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_precio(mensaje: str, user: str) -> dict:
    prompt = f"""
Extraé los datos para registrar precios por litro de cerveza a partir del siguiente mensaje.

🔸 Si el mensaje se refiere a "todos los estilos", "todos los productos", o una expresión similar, devolvé una lista de registros, uno por cada estilo de cerveza.

📌 Estilos válidos (usar exactamente estos nombres):
["session ipa", "ipa patagonica", "black ipa", "red ipa", "cream ale", "honey", "maracujapa", "pilsen"]

📌 Si el mensaje menciona un estilo que **no coincide exactamente** con estos nombres, asumí el más probable y devolvé el campo `producto` exactamente como está escrito en la lista.

📌 Campos requeridos en cada registro:
- producto (uno de los estilos válidos, exactamente como en la lista)
- formato (por ejemplo: "botella", "barril")
- precio_litro (valor numérico en reales)

📌 Ejemplo de mensaje:
"El precio por litro en botella de todos los estilos es 25 reales."

✅ Ejemplo de respuesta esperada:
```json
[
  {"producto": "session ipa", "formato": "botella", "precio_litro": 25},
  {"producto": "ipa patagonica", "formato": "botella", "precio_litro": 25},
  ...
]

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