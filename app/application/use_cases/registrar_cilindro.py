

from app.domain.models.cilindro import Cilindro
from app.infrastructure.repositories.cilindro_repo import CilindroRepository
from datetime import datetime

def registrar_cilindro(data: dict, repo: CilindroRepository) -> str:
    """
    Registra un nuevo cilindro de CO2 en el sistema.

    Args:
        data (dict): Datos del cilindro con las claves:
            - identificador_cilindro (int)
            - capacidad (float) en kg
            - peso_vacio (float) en kg
            - ubicacion (str): 'fábrica' o 'cliente'
            - porcentaje_carga (float, opcional)
            - id_cliente (int, opcional, si ubicacion == 'cliente')

        repo (CilindroRepository): Repositorio de persistencia

    Returns:
        str: Mensaje de confirmación o error
    """
    try:
        if "porcentaje_carga" not in data:
            data["porcentaje_carga"] = 0.0

        cilindro = Cilindro(
            identificador_cilindro=data["identificador_cilindro"],
            capacidad=data["capacidad"],
            peso_vacio=data["peso_vacio"],
            porcentaje_carga=data["porcentaje_carga"],
            ubicacion=data["ubicacion"],
            id_cliente=data.get("id_cliente"),
            fecha_alta=datetime.utcnow(),
            fecha_control=datetime.utcnow(),
        )

        repo.guardar(cilindro)
        return f"Cilindro {data['identificador_cilindro']} registrado correctamente."

    except Exception as e:
        return f"Error al registrar cilindro: {str(e)}"