

from app.domain.models.botella import Botella
from app.infrastructure.repositories.botella_repo import BotellaRepository
from datetime import datetime

class RegistrarBotellaUseCase:
    def __init__(self, repository: BotellaRepository):
        self.repository = repository

    def execute(self, identificador_botella: int, capacidad_litros: float, ubicacion: str, estado: str = "vacía"):
        botella = Botella(
            identificador_botella=identificador_botella,
            capacidad_litros=capacidad_litros,
            estado=estado,
            ubicacion=ubicacion,
            fecha_alta=datetime.now()
        )
        self.repository.add(botella)
        return {"status": "ok", "message": f"Botella {identificador_botella} registrada correctamente"}