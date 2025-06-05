# app/interfaces/parsers/fermentador.py
from app.infrastructure.openai.client import openai_client
import json
from app.infrastructure.config import get_settings

settings = get_settings()

async def parse_fermentador(mensaje: str, user: str) -> dict:
    prompt = f"""
Extraé los datos para registrar un fermentador a partir del siguiente mensaje. Este proceso forma parte de la carga administrativa inicial de los 7 fermentadores existentes en la cervecería.

Campos requeridos:
- identificador (número del fermentador, por ejemplo 3)
- capacidad_litros (valor numérico, puede expresarse como "300 litros")
- estado_actual (por ejemplo: vacío, lleno, en fermentación, etc.)
- ubicacion (opcional, puede ser 'fábrica' o 'cliente')

Ejemplo de mensaje:
"El fermentador número 3, con capacidad de 300 litros, se encuentra actualmente vacío."

⚠️ Importante:
- Solo se registrará un fermentador por vez.
- Extraé los datos aunque estén en otro orden o redactados informalmente.
- Convertí la capacidad a valor numérico sin unidades.
- Devolvé el JSON sin explicaciones, sin comentarios, sin texto adicional.
- No uses bloques de markdown como ```json.
- Asegurate de que los nombres y estados estén bien escritos para evitar registros inconsistentes.

Este registro será utilizado para habilitar los fermentadores en el sistema de gestión operativa.

Mensaje:
\"\"\"{mensaje}\"\"\"
"""

    try:
        response = await openai_client.chat.completions.create(
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

        datos = json.loads(contenido)

        campos_obligatorios = ["identificador", "capacidad_litros", "estado_actual"]
        faltantes = [campo for campo in campos_obligatorios if campo not in datos or not datos[campo]]
        return {
            "ok": len(faltantes) == 0,
            "faltantes": faltantes,
            "datos": datos,
            "tabla_destino": "Fermentador"
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": {}
        }