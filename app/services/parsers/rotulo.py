import openai
import json
from app.core.config import get_settings
from app.db.database import SessionLocal
from app.db.models import Producto
from app.utils.productos import get_product_id

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_rotulo(mensaje: str, user: str) -> dict:
    session = SessionLocal()
    try:
        productos_validos = [p.nombre.lower() for p in session.query(Producto).all()]
    finally:
        session.close()

    prompt = f"""
    Extraé los datos para registrar un ingreso de rótulos desde el siguiente mensaje.

    Campos requeridos:
    - producto (nombre del estilo, por ejemplo: IPA, Cream Ale, etc.)
    - cantidad (cantidad de rótulos ingresados, número entero)

    Devolvé un JSON con esos campos. El producto debe ser uno de los siguientes: {productos_validos}

    Mensaje:
    \"\"\"{mensaje}\"\"\"

    Respondé solo con el JSON, sin texto adicional.
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

        producto_nombre = datos.get("producto", "").lower()
        id_producto = get_product_id(producto_nombre)
        if not id_producto:
            return {
                "ok": False,
                "error": f"Producto '{producto_nombre}' no encontrado en la base de datos.",
                "datos": {},
            }
        datos["id_producto"] = id_producto
        datos.pop("producto", None)

        faltantes = [campo for campo in ["id_producto", "cantidad"] if campo not in datos or not datos[campo]]

        return {
            "ok": len(faltantes) == 0,
            "faltantes": faltantes,
            "datos": datos,
            "tabla_destino": "Rotulo"
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": {},
        }