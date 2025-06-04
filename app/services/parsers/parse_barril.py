# app/services/parsers/parse_barril.py
import openai
import json
from app.core.config import get_settings

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_barril(mensaje: str, user: str) -> dict:
    prompt = f"""
Extraé la información de todos los barriles mencionados en el siguiente mensaje.

📌 Para cada barril, devolvé un objeto con los siguientes campos:

- id (número del barril)
- volumen_litros (por ejemplo: 30, 50)
- producto (nombre del estilo de cerveza, puede estar vacío si no se especifica)
- lote (número de lote si estuviera presente, opcional)
- estado (por ejemplo: lleno, vacío, limpio, sucio. Usá 'desconocido' si no se indica)
- ubicacion (por ejemplo: fábrica, cámara, cliente, etc. Usá 'desconocida' si no se indica)

🧠 Si hay varios barriles listados con diferentes volúmenes o estados, devolvé un array de objetos, uno por cada barril.

📌 Ejemplo de mensaje:
"Ingresaron los barriles 101, 102 y 103, todos vacíos, de 50 litros. El 104 y 105 están llenos con APA, lote 400."

📌 Ejemplo de respuesta:
[
  {"id": 101, "volumen_litros": 50, "producto": "", "lote": null, "estado": "vacío", "ubicacion": "desconocida"},
  {"id": 102, "volumen_litros": 50, "producto": "", "lote": null, "estado": "vacío", "ubicacion": "desconocida"},
  {"id": 103, "volumen_litros": 50, "producto": "", "lote": null, "estado": "vacío", "ubicacion": "desconocida"},
  {"id": 104, "volumen_litros": 50, "producto": "APA", "lote": 400, "estado": "lleno", "ubicacion": "desconocida"},
  {"id": 105, "volumen_litros": 50, "producto": "APA", "lote": 400, "estado": "lleno", "ubicacion": "desconocida"}
]

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

        faltantes = [campo for campo in ["id_interno", "volumen_litros", "formato"] if campo not in datos or not datos[campo]]

        return {
            "ok": len(faltantes) == 0,
            "faltantes": faltantes,
            "datos": datos,
            "tabla_destino": "Barril"
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": {}
        }