

from app.domain.models.fermentador import Fermentador
from app.infrastructure.repositories.fermentador_repo import FermentadorRepository
from datetime import datetime


def registrar_fermentador(data: dict) -> str:
    try:
        identificador = int(data["identificador"])
        capacidad_litros = float(data["capacidad_litros"])
        ubicacion = data.get("ubicacion", "fábrica")
        estado_actual = data.get("estado_actual", "vacío")

        fermentador = Fermentador(
            identificador_fermentador=identificador,
            capacidad_litros=capacidad_litros,
            estado_actual=estado_actual,
            fecha_alta=datetime.utcnow(),
            ubicacion=ubicacion
        )

        repo = FermentadorRepository()
        if repo.exists(identificador):
            return f"Ya existe un fermentador con identificador físico {identificador}."
        
        repo.save(fermentador)
        return f"Fermentador {identificador} registrado correctamente."

    except KeyError as e:
        return f"Falta el campo requerido: {str(e)}"
    except Exception as e:
        return f"Error al registrar fermentador: {str(e)}"