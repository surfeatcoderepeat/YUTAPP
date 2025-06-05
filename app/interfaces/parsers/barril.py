from datetime import datetime
import json
from app.infrastructure.openai.client import openai_client
from app.infrastructure.repositories.producto_repo import get_producto_id
from app.infrastructure.repositories.lote_repo import get_lote_id

async def parse_barril(mensaje: str, user: str) -> dict:
    prompt = f"""
Extraé la información del barril mencionado en el siguiente mensaje.

📌 Devolvé un objeto con los siguientes campos:
    - id (número del barril)
    - volumen_litros
    - producto (opcional)
    - lote (opcional)
    - estado (lleno, vacío, limpio, sucio, o 'desconocido')
    - ubicacion ('fábrica', 'cliente', o 'desconocida')

🧠 Si no hay información suficiente, completá con null.

📌 Ejemplo de mensaje:
"Ingresó el barril 101 vacío, de 50 litros."

📌 Ejemplo de respuesta:
{"id": 101, "volumen_litros": 50, "producto": "", "lote": null, "estado": "vacío", "ubicacion": "desconocida"}

Mensaje:
\"\"\"{mensaje}\"\"\"

Devolvé solo un JSON válido.
    """

    try:
        contenido = await openai_client.extract_fields(mensaje, prompt)
        barril = json.loads(contenido)

        if not isinstance(barril, dict):
            return {"ok": False, "error": "La respuesta del modelo no es un objeto.", "datos": {}}

        producto = barril.get("producto", "").strip().lower()
        barril["id_producto"] = get_producto_id(producto) if producto else None
        if producto and barril["id_producto"] is None:
            return {"ok": False, "error": f"Producto '{producto}' no encontrado.", "datos": {}}

        if barril.get("lote") is not None and barril.get("id_producto") is not None:
            barril["id_lote"] = get_lote_id(barril["lote"], barril["id_producto"])
            if barril["id_lote"] is None:
                return {"ok": False, "error": f"Lote {barril['lote']} no válido para producto '{producto}'", "datos": {}}

        barril.pop("producto", None)

        faltantes = [campo for campo in ["id", "volumen_litros", "estado", "ubicacion", "id_producto"] if barril.get(campo) is None]
        if faltantes:
            return {"ok": False, "faltantes": faltantes, "datos": {}}

        return {"ok": True, "datos": barril, "tabla_destino": "barril"}

    except Exception as e:
        return {"ok": False, "error": str(e), "datos": {}}