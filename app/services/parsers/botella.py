# app/services/parsers/botella.py
import openai
import json
from app.core.config import get_settings
from app.utils.productos import get_producto_id
from app.utils.lotes import get_lote_id

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_botella(mensaje: str, user: str) -> dict:
    prompt = f"""
Extraé los datos para registrar ingresos de botellas a partir del siguiente mensaje. 
Puede haber múltiples registros en una misma frase. Cada registro debe incluir:

- volumen_litros (volumen en litros, como 0.33, 0.6, etc.)
- cantidad (número de botellas)
- estado (vacía, limpia, sucia, etc.)
- ubicacion (como "stock fábrica")
- producto (nombre del producto)
- lote (identificador del lote)

Mensaje:
\"\"\"{mensaje}\"\"\"

Devolvé una lista JSON con un objeto por cada tipo de botella. No incluyas explicaciones, solo el JSON.
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

        datos = json.loads(contenido)

        if not isinstance(datos, list):
            datos = [datos]

        campos_requeridos = ["volumen_litros", "cantidad", "estado", "ubicacion", "id_producto", "id_lote"]
        faltantes = []

        for entry in datos:
            # Validar y convertir producto a id_producto
            producto = entry.get("producto")
            if producto:
                id_producto = await get_producto_id(producto)
                if id_producto is not None:
                    entry["id_producto"] = id_producto
                else:
                    faltantes.append("id_producto")
            else:
                faltantes.append("id_producto")

            # Validar y convertir lote a id_lote
            lote = entry.get("lote")
            if lote:
                id_lote = await get_lote_id(lote)
                if id_lote is not None:
                    entry["id_lote"] = id_lote
                else:
                    faltantes.append("id_lote")
            else:
                faltantes.append("id_lote")

            # Eliminar producto y lote después de la conversión
            if "producto" in entry:
                del entry["producto"]
            if "lote" in entry:
                del entry["lote"]

            for campo in campos_requeridos:
                if campo not in entry or not entry[campo]:
                    faltantes.append(campo)

        return {
            "ok": len(faltantes) == 0,
            "faltantes": list(set(faltantes)),
            "datos": datos,
            "tabla_destino": "Botella"
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": []
        }
