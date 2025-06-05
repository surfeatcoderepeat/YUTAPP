

from app.domain.models.rotulo import Rotulo
from app.infrastructure.repositories.rotulo_repo import RotuloRepository

class RegistrarRotuloUseCase:
    def __init__(self, rotulo_repository: RotuloRepository):
        self.rotulo_repository = rotulo_repository

    def execute(self, nombre_producto: str, cantidad: int, fecha: str, responsable: str) -> Rotulo:
        nuevo_rotulo = Rotulo(
            nombre_producto=nombre_producto,
            cantidad=cantidad,
            fecha=fecha,
            responsable=responsable
        )
        self.rotulo_repository.guardar(nuevo_rotulo)
        return nuevo_rotulo