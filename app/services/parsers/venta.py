import openai
import json
from app.core.config import get_settings
from app.utils.productos import get_producto_id
from app.utils.clientes import get_cliente_id_por_nombre

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_venta(mensaje: str, user: str) -> dict:
    productos = None  # ya no se usa un diccionario local
    clientes = None   # ya no se usa un diccionario local

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

        producto_id = get_producto_id(datos.get("producto", ""))
        if not producto_id:
            errores.append("producto inválido")
        else:
            datos["id_producto"] = producto_id

        cliente_id = get_cliente_id_por_nombre(datos.get("nombre_cliente", ""))
        if not cliente_id:
            errores.append("cliente no registrado")
        else:
            datos["id_cliente"] = cliente_id

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