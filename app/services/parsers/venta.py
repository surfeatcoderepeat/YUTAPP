import openai
import json
from app.core.config import get_settings
from app.db.database import SessionLocal
from app.db.models import Producto, Cliente
from app.utils.validations import get_product_id

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_venta(mensaje: str, user: str) -> dict:
    session = SessionLocal()

    # Obtener lista de productos y clientes válidos
    productos = {p.nombre.lower(): p.id for p in session.query(Producto).all()}
    clientes = {c.nombre.lower(): c.id for c in session.query(Cliente).all()}

    prompt = f"""
Extraé los datos para registrar una venta de cerveza en una fábrica artesanal.

Campos requeridos:
- producto (por ejemplo: APA, IPA, etc.)
- formato (por ejemplo: botella o barril)
- volumen_litros (por unidad, como 20, 30 o 50)
- cantidad (cuántos productos iguales se entregan o piden)
- nombre_cliente (nombre del cliente que debe coincidir con uno de los registrados)
- fecha_pedido (si se menciona, o usar la fecha actual si no)
- fecha_cobro (si se menciona)
- responsable (quien ejecuta o registra la acción)

Mensaje:
\"\"\"{mensaje}\"\"\"

Respondé únicamente con un JSON. No incluyas explicaciones, ni encabezados tipo ```json.
    """

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.2,
        )
        contenido = response.choices[0].message.content

        datos = json.loads(contenido)

        # Normalización y validación
        errores = []

        if "producto" not in datos or get_product_id(datos["producto"], productos) is None:
            errores.append("producto inválido")
        else:
            datos["id_producto"] = get_product_id(datos["producto"], productos)
        if "nombre_cliente" not in datos or datos["nombre_cliente"].lower() not in clientes:
            errores.append("cliente no registrado")
        if "volumen_litros" not in datos or not isinstance(datos["volumen_litros"], (int, float)):
            errores.append("volumen_litros faltante o inválido")
        if "cantidad" not in datos or not isinstance(datos["cantidad"], int):
            errores.append("cantidad faltante o inválida")
        if "formato" not in datos or datos["formato"] not in ["botella", "barril"]:
            errores.append("formato inválido")

        if "fecha_cobro" in datos and not isinstance(datos["fecha_cobro"], str):
            errores.append("fecha_cobro inválida")

        if errores:
            return {
                "ok": False,
                "faltantes": errores,
                "datos": {}
            }

        datos["id_cliente"] = clientes[datos["nombre_cliente"].lower()]
        datos["precio_unitario"] = 0  # Se puede actualizar después desde precios
        datos["precio_total"] = 0     # Se calcula más adelante

        # Quitar campos redundantes
        datos.pop("nombre_cliente", None)
        datos.pop("producto", None)

        resultado = {
            "ok": True,
            "datos": datos,
            "tabla_destino": "Venta"
        }

        return resultado

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": {}
        }

    finally:
        session.close()