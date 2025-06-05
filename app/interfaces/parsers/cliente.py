# app/interfaces/parsers/cliente.py
import openai
import json
from app.infrastructure.openai.client import openai_client  # Uso estándar del cliente OpenAI para todos los parsers
from datetime import datetime, timezone
from app.domain.models.cliente import Cliente
from app.infrastructure.repositories.cliente_repo import guardar_cliente

async def parse_cliente(mensaje: str, user: str) -> dict:
    prompt = f"""
Extraé los datos para registrar uno o más clientes a partir del siguiente mensaje. El mensaje puede contener un inventario de clientes listados con nombre y CNPJ o CPF. Interpretá correctamente cada cliente y devolvé uno por cada línea, si aplica.

Por cada cliente, devolvé un objeto con los siguientes campos:
- nombre (nombre del cliente)
- cnpj_cpf (si estuviera presente, opcional)

Si hay varios clientes, devolvé una lista de objetos. Si hay solo uno, devolvelo igual en una lista.

IMPORTANTE:
- Usá los nombres tal como deben guardarse en la base de datos (sin errores de tipeo).
- Devolvé solo el JSON sin explicaciones, sin comentarios, sin texto adicional.
- No incluyas bloques tipo markdown (nada de ```json).

Mensaje:
\"\"\"{mensaje}\"\"\"
"""

    try:
        response = await openai_client.acreate(
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

        if not isinstance(datos, list):
            datos = [datos]

        for cliente in datos:
            nombre = cliente.get("nombre", "").strip().title()
            if not nombre:
                continue
            cnpj_cpf = str(cliente.get("cnpj_cpf")) if "cnpj_cpf" in cliente else ""
            nuevo_cliente = Cliente(
                nombre=nombre,
                documento=cnpj_cpf,
                creado_por=user,
                fecha_alta=datetime.now(timezone.utc)
            )
            guardar_cliente(nuevo_cliente)

        return {
            "ok": True,
            "faltantes": [],
            "datos": datos,
            "tabla_destino": "Cliente"
        }

    except Exception as e:
        return {
            "ok": False,
            "error": str(e),
            "datos": {}
        }