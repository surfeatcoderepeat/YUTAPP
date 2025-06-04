import openai
import json
from app.core.config import get_settings
from app.utils.productos import get_producto_id

settings = get_settings()
openai.api_key = settings.openai_api_key

async def parse_precio(mensaje: str, user: str) -> dict:

    prompt = f"""
Sos un asistente que debe procesar mensajes para cargar precios de cerveza por litro en una base de datos. 
El usuario puede enviar precios generales para todos los estilos, o específicos para estilos IPA o no IPA, y también por formato (botella o barril).

Indicá estilos conocidos cargados previamente por el usuario.
Formatos posibles: botella, barril

Ejemplo 1:
"El precio para cualquier tipo de botella y cualquier estilo es 25 reales por litro."

Ejemplo 2:
"El precio para las IPAs en barril es de 20 reales, y para el resto es de 18 reales por litro."

Mensaje:
\"\"\"{mensaje}\"\"\"

Devolvé un JSON con una lista bajo la clave "precios", donde cada precio es un diccionario con:
- producto (el nombre exacto del estilo)
- formato (botella o barril)
- precio_litro (número entero o decimal)

NO devuelvas explicaciones ni markdown, solo un JSON válido.
"""

    try:
        response = await openai.ChatCompletion.acreate(
            model="gpt-4o",
            messages=[{"role": "user", "content": prompt}],
            temperature=0.3,
        )

        contenido = response.choices[0].message.content

        # Limpia bloques de markdown tipo ```json ... ```
        if contenido.strip().startswith("```"):
            contenido = "\n".join(
                line for line in contenido.strip().splitlines()
                if not line.strip().startswith("```")
            )

        json_data = json.loads(contenido)
        precios = json_data.get("precios", [])

        # Validación y control de estilos
        precios_limpios = []
        faltantes = []

        for entrada in precios:
            estilo = entrada.get("producto", "").lower()
            formato = entrada.get("formato", "").lower()

            if formato not in ["botella", "barril"]:
                faltantes.append(f"formato inválido: {formato}")
                continue

            id_producto = get_producto_id(estilo)
            if id_producto is None:
                faltantes.append(f"producto no encontrado: {estilo}")
                continue

            precios_limpios.append({
                "id_producto": id_producto,
                "formato": formato,
                "precio_litro": entrada.get("precio_litro")
            })

        return {
            "ok": len(precios_limpios) > 0,
            "faltantes": faltantes,
            "datos": precios_limpios,
            "tabla_destino": "Precio"
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": []
        }
