

from app.domain.models.barril import Barril
from app.infrastructure.repositories.barril_repo import BarrilRepository
from datetime import datetime


class RegistrarBarrilUseCase:
    def __init__(self, barril_repo: BarrilRepository):
        self.barril_repo = barril_repo

    def execute(self, identificador_barril: int, volumen_litros: float, ubicacion: str, estado: str = "vacío"):
        nuevo_barril = Barril(
            identificador_barril=identificador_barril,
            volumen_litros=volumen_litros,
            ubicacion=ubicacion,
            estado=estado,
            fecha_alta=datetime.utcnow()
        )
        self.barril_repo.save(nuevo_barril)
        return {"status": "ok", "barril_id": nuevo_barril.identificador_barril}