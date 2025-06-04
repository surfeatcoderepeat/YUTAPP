import openai
import json
from datetime import datetime
from app.core.config import get_settings
from app.utils.productos import get_producto_id
from app.utils.fermentadores import existe_fermentador
from app.utils.lotes import existe_lote_id, crear_lote_si_no_existe

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

        if "responsable" not in datos or not datos["responsable"]:
            datos["responsable"] = user

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

            # Si es un llenado y el lote no existe, lo creamos automáticamente
            if datos.get("tipo_evento") == "llenado" and not existe_lote_id(datos["id_lote"]):
                print(f"[DEBUG] Lote {datos['id_lote']} no existe, se creará automáticamente...")
                nuevo_id = crear_lote_si_no_existe(
                    descripcion=f"Lote {datos['id_lote']}",
                    id_fermentador=datos.get("id_fermentador")
                )
                datos["id_lote"] = nuevo_id
                datos["mensaje_lote_creado"] = f"✅ Lote {nuevo_id} creado automáticamente."

        # Fermentador
        if "id_fermentador" in datos and not existe_fermentador(datos["id_fermentador"]):
            errores.append(f"Fermentador {datos['id_fermentador']} no encontrado")

        # Fecha
        if "fecha" not in datos or not datos["fecha"] or datos["fecha"].strip().lower() == "hoy":
            datos["fecha"] = datetime.now().strftime("%Y-%m-%d")

        # No eliminamos el campo 'observaciones' para que quede en datos

        # Si no hay 'descripcion' pero sí 'observaciones', usar 'observaciones' como descripcion
        if "descripcion" not in datos and "observaciones" in datos:
            datos["descripcion"] = datos["observaciones"]

        # Filtramos solo los campos válidos para el modelo RegistroFermentador
        campos_validos = {"fecha", "id_lote", "id_fermentador", "tipo_evento", "descripcion", "responsable", "id_producto"}
        datos = {k: v for k, v in datos.items() if k in campos_validos}

        respuesta = {
            "ok": len(errores) == 0,
            "datos": datos,
            "faltantes": errores,
            "tabla_destino": "RegistroFermentador",
        }

        if respuesta["ok"]:
            lote = datos.get("id_lote", "?")
            litros = datos.get("descripcion", "").split(" ")[0] if "litros" in datos.get("descripcion", "") else "?"
            producto = datos.get("id_producto", "producto desconocido")
            fermentador = datos.get("id_fermentador", "?")
            estado = datos.get("tipo_evento", "?")
            responsable = datos.get("responsable", "?")
            
            respuesta["mensaje_usuario"] = (
                f"✅ Registro exitoso: {litros} litros de {producto} en el fermentador {fermentador} "
                f"(lote {lote}), etapa: {estado}, registrado por {responsable}."
            )

        return respuesta

    except Exception as e:
        error_msg = str(e)
        if "violates foreign key constraint" in error_msg and "id_lote" in error_msg:
            error_msg = "Verificá el número de lote: no se encontró ningún lote registrado con ese ID."
        return {
            "ok": False,
            "error": error_msg,
            "datos": {},
        }