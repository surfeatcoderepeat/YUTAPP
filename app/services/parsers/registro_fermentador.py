import openai
import json
from datetime import datetime
from app.core.config import get_settings
from app.db.database import SessionLocal
from app.db.models import Producto, Lote, Fermentador

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_registro_fermentador(mensaje: str, user: str) -> dict:
    prompt = f"""
Sos un sistema que registra intervenciones en fermentadores para una cervecería artesanal. 
Cada línea de registro representa un evento como llenado, toma de muestra, adición de lúpulo o fruta, embarrilado o limpieza.

Debés extraer los siguientes campos en formato JSON:
- id_fermentador (número de fermentador)
- id_producto (nombre del producto, si lo hay)
- id_lote (número del lote, si lo hay)
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

        # Validaciones
        session = SessionLocal()
        errores = []

        # Producto
        if "id_producto" in datos:
            nombre_producto = datos["id_producto"]
            producto = session.query(Producto).filter(Producto.nombre.ilike(nombre_producto)).first()
            if producto:
                datos["id_producto"] = producto.id
            else:
                errores.append(f"Producto '{nombre_producto}' no registrado")

        # Lote
        if "id_lote" in datos:
            id_lote = datos["id_lote"]
            lote = session.query(Lote).filter(Lote.id == id_lote).first()
            if not lote:
                errores.append(f"Lote {id_lote} no encontrado")

        # Fermentador
        if "id_fermentador" in datos:
            id_f = datos["id_fermentador"]
            fermentador = session.query(Fermentador).filter(Fermentador.id == id_f).first()
            if not fermentador:
                errores.append(f"Fermentador {id_f} no encontrado")

        # Fecha
        if "fecha" not in datos or not datos["fecha"]:
            datos["fecha"] = datetime.now().strftime("%Y-%m-%d")

        session.close()

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