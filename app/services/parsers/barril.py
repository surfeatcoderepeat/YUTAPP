# app/services/parsers/parse_barril.py
import openai
import json
from datetime import datetime
from app.core.config import get_settings
from app.utils.productos import get_producto_id
from app.utils.lotes import get_lote_id

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
- ubicacion (puede ser 'fábrica' o 'cliente'. Inferilo según el contexto del mensaje. Si no queda claro, usá 'desconocida')

🧠 Si hay varios barriles listados con diferentes volúmenes o estados, devolvé un array de objetos, uno por cada barril.

📌 Ejemplo de mensaje:
"Ingresaron los barriles 101, 102 y 103, todos vacíos, de 50 litros. El 104 y 105 están llenos con APA, lote 400."

📌 Ejemplo de respuesta:
[
  {{"id": 101, "volumen_litros": 50, "producto": "", "lote": null, "estado": "vacío", "ubicacion": "desconocida"}},
  {{"id": 102, "volumen_litros": 50, "producto": "", "lote": null, "estado": "vacío", "ubicacion": "desconocida"}},
  {{"id": 103, "volumen_litros": 50, "producto": "", "lote": null, "estado": "vacío", "ubicacion": "desconocida"}},
  {{"id": 104, "volumen_litros": 50, "producto": "APA", "lote": 400, "estado": "lleno", "ubicacion": "desconocida"}},
  {{"id": 105, "volumen_litros": 50, "producto": "APA", "lote": 400, "estado": "lleno", "ubicacion": "desconocida"}}
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

        if not isinstance(datos, list):
            return {
                "ok": False,
                "error": "La respuesta del modelo no es una lista.",
                "datos": {}
            }

        for barril in datos:
            nombre_producto = barril.get("producto", "").strip().lower()
            if nombre_producto:
                barril["id_producto"] = get_producto_id(nombre_producto)
                if barril["id_producto"] is None:
                    return {
                        "ok": False,
                        "error": f"Producto '{nombre_producto}' no encontrado en base de datos.",
                        "datos": {}
                    }
            else:
                barril["id_producto"] = None

        for barril in datos:
            if "lote" in barril and barril["lote"] is not None and barril.get("id_producto") is not None:
                lote_id = get_lote_id(barril["lote"], barril["id_producto"])
                if lote_id is None:
                    return {
                        "ok": False,
                        "error": f"Lote {barril['lote']} no válido para producto '{barril.get('producto', '')}'",
                        "datos": {}
                    }
                barril["id_lote"] = lote_id

        # Eliminar campo producto del resultado final
        for barril in datos:
            barril.pop("producto", None)

        faltantes = []
        for barril in datos:
            for campo in ["id", "volumen_litros", "estado", "ubicacion", "id_producto"]:
                if campo not in barril or barril[campo] is None:
                    faltantes.append(f"{campo} en barril {barril.get('id', '?')}")

        if faltantes:
            return {
                "ok": False,
                "faltantes": faltantes,
                "datos": {},
            }

        # Preparar registro para RegistroFermentador
        # Tomar id_lote e id_producto del primer barril que tenga ambos
        id_lote = None
        id_producto = None
        volumen_total = 0
        for barril in datos:
            if barril.get("id_lote") is not None and barril.get("id_producto") is not None:
                id_lote = barril["id_lote"]
                id_producto = barril["id_producto"]
            volumen_total += barril.get("volumen_litros", 0)

        if id_lote is None or id_producto is None:
            return {
                "ok": False,
                "error": "No se pudo determinar id_lote o id_producto para el registro de fermentador.",
                "datos": {}
            }

        registro_fermentador = {
            "fecha": datetime.now().strftime("%Y-%m-%d"),
            "id_lote": id_lote,
            "id_producto": id_producto,
            "tipo_evento": "embarrilado",
            "descripcion": f"Se embarrilaron {len(datos)} barriles - total {volumen_total}L",
            "responsable": user
        }

        return {
            "ok": True,
            "datos": {
                "barriles": datos,
                "registro_fermentador": registro_fermentador
            },
            "tabla_destino": "multiple"
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": {}
        }