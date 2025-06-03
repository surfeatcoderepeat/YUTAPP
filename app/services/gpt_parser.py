# app/services/gpt_parser.py
import openai
import json
from app.core.config import get_settings

settings = get_settings()
openai.api_key = settings.openai_api_key

# Campos que esperamos extraer
CAMPOS_REQUERIDOS = [
    "tipo", "producto", "formato", "volumen_litros", "lote",
    "cliente", "responsable", "mensaje_original"
]

# Si el formato es barril, también queremos 'id_barril'
def necesita_id_barril(formato: str) -> bool:
    return formato.strip().lower() == "barril"

async def interpretar_mensaje(mensaje: str, user: str) -> dict:
    prompt = f"""
Extraé del siguiente mensaje todos los campos necesarios para registrar un movimiento de stock de cerveza artesanal.

Campos requeridos:
- tipo (ej: 'salida', 'entrada')
- producto (ej: 'IPA', 'APA')
- formato (ej: 'barril', 'botella')
- volumen_litros (número en litros, ej: 50.0)
- lote (numer entero)
- cliente (nombre)
- responsable (usuario que lo envía: '{user}')
- id_barril (solo si el formato es 'barril', número entero)
- observacion (si el mensaje la contiene)
- mensaje_original (devolvé el mensaje completo sin cambios)

Mensaje:
\"\"\"{mensaje}\"\"\"
Devolvé solo un JSON limpio, estrictamente válido, sin comentarios ni explicaciones.
    """

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        contenido = response.choices[0].message.content
        if not contenido or not contenido.strip():
            return {
                "ok": False,
                "error": "Respuesta vacía de la API de OpenAI",
                "datos": {}
            }
        datos = json.loads(contenido)  # ⚠️ puede reemplazarse por json.loads() si es formato válido

        # Validación: todos los campos presentes
        faltantes = [campo for campo in CAMPOS_REQUERIDOS if campo not in datos or not datos[campo]]
        if datos.get("formato", "").lower() == "barril" and "id_barril" not in datos:
            faltantes.append("id_barril")

        return {
            "ok": len(faltantes) == 0,
            "faltantes": faltantes,
            "datos": datos
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": {}
        }