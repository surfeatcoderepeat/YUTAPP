from app.infrastructure.openai.client import openai_client
from app.infrastructure.repositories.lote_repo import LoteRepository
from app.infrastructure.repositories.producto_repo import ProductoRepository
from app.infrastructure.repositories.fermentador_repo import FermentadorRepository
from app.application.use_cases.registrar_lote import RegistrarLoteUseCase

def parse_register_lote(message: str, user: str):
    """
    Extrae datos desde el mensaje para registrar un nuevo lote, utilizando OpenAI.
    """
    system_prompt = """
    Extraé los siguientes campos desde un mensaje de texto:
    - producto (nombre del estilo de cerveza)
    - numero_lote (número de lote, entero)
    - identificador_fermentador (identificador físico del fermentador, entero)
    Retorná un JSON con los campos:
    {
        "producto": "string",
        "numero_lote": int,
        "identificador_fermentador": int
    }
    """

    response = openai_client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": message}
        ],
        temperature=0.0
    )

    data = response.choices[0].message.content

    try:
        parsed = eval(data)
        use_case = RegistrarLoteUseCase(
            lote_repo=LoteRepository(),
            producto_repo=ProductoRepository(),
            fermentador_repo=FermentadorRepository()
        )
        return use_case.execute(
            producto_nombre=parsed["producto"],
            numero=int(parsed["numero_lote"]),
            identificador_fermentador=int(parsed["identificador_fermentador"])
        )
    except Exception as e:
        return f"Error al interpretar el mensaje: {e}"