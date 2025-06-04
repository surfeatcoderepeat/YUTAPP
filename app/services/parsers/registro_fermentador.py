import openai
import json
from datetime import datetime
from app.core.config import get_settings
from app.utils.productos import get_producto_id
from app.utils.fermentadores import existe_fermentador

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_registro_fermentador(mensaje: str, user: str) -> dict:
    prompt = f"""
Sos un sistema que registra intervenciones en fermentadores para una cervecería artesanal. 
Cada línea de registro representa un evento como llenado, toma de muestra, adición de lúpulo o fruta, embarrilado o limpieza.

Debés extraer los siguientes campos en formato JSON:
- id_fermentador (número de fermentador)
- id_producto (nombre del producto, si lo hay)
- id_lote (número del lote si lo hay, no usar nombres)
- fecha (fecha del evento en formato YYYY-MM-DD o 'hoy' si no se menciona)
- etapa (puede ser llenado, muestra, adición, embarrilado, limpieza u otra)
- observaciones (detalles adicionales que ayuden a interpretar el evento)
- responsable (nombre de quien hace el registro)

Ejemplo de mensaje:
"Hoy llenamos el fermentador 4 con el lote 108 de Cream Ale. Responsable: Tincho."

Mensaje:
\"\"\"{mensaje}\"\"\"

Devolvé solo un JSON válido, sin explicaciones ni comentarios.
"""

    try:
        print("[DEBUG] Enviando prompt a OpenAI...")
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )

        contenido = response.choices[0].message.content.strip()

        if contenido.startswith("```"):
            contenido = "\n".join(
                line for line in contenido.splitlines()
                if not line.strip().startswith("```")
            )

        print(f"[DEBUG] Contenido limpio: {contenido}")
        datos = json.loads(contenido)
        if "etapa" in datos:
            datos["tipo_evento"] = datos.pop("etapa")

        errores = []

        # Producto
        if "id_producto" in datos:
            try:
                datos["id_producto"] = get_producto_id(datos["id_producto"])
            except ValueError as e:
                errores.append(str(e))

        # Lote
        if "id_lote" in datos:
            try:
                datos["id_lote"] = int(datos["id_lote"])
            except:
                errores.append("id_lote inválido o no numérico")

        # Fermentador
        if "id_fermentador" in datos and not existe_fermentador(datos["id_fermentador"]):
            errores.append(f"Fermentador {datos['id_fermentador']} no encontrado")

        # Fecha
        if "fecha" not in datos or not datos["fecha"]:
            datos["fecha"] = datetime.now().isoformat()
        else:
            try:
                datos["fecha"] = datetime.strptime(datos["fecha"], "%Y-%m-%d").isoformat()
            except Exception:
                errores.append("Formato de fecha inválido. Usar YYYY-MM-DD o 'hoy'")

        # No eliminamos el campo 'observaciones' para que quede en datos

        # Filtramos solo los campos válidos para el modelo RegistroFermentador
        campos_validos = {"fecha", "id_lote", "id_fermentador", "tipo_evento", "descripcion", "responsable", "id_producto"}
        datos = {k: v for k, v in datos.items() if k in campos_validos}

        return {
            "ok": len(errores) == 0,
            "datos": datos,
            "faltantes": errores,
            "tabla_destino": "RegistroFermentador",
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": {},
        }