from datetime import date
import openai
import json
from app.infrastructure.config import get_settings
from app.domain.models.producto import get_productos_validos, get_producto_id

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_rotulo(mensaje: str, user: str) -> dict:
    productos_validos = get_productos_validos()

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
        id_producto = get_producto_id(producto_nombre)
        if not id_producto:
            return {
                "ok": False,
                "error": f"Producto '{producto_nombre}' no encontrado en la base de datos.",
                "datos": {},
            }

        datos_finales = {
            "nombre_producto": producto_nombre,
            "cantidad": datos.get("cantidad"),
            "fecha": date.today().isoformat(),
            "responsable": user
        }

        faltantes = [campo for campo in ["nombre_producto", "cantidad", "fecha", "responsable"] if not datos_finales.get(campo)]

        return {
            "ok": len(faltantes) == 0,
            "faltantes": faltantes,
            "datos": datos_finales,
            "tabla_destino": "Rotulo"
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": {},
        }