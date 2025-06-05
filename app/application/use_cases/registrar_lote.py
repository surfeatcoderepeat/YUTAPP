

from app.infrastructure.repositories.lote_repo import LoteRepository
from app.infrastructure.repositories.producto_repo import ProductoRepository
from app.infrastructure.repositories.fermentador_repo import FermentadorRepository
from datetime import date


class RegistrarLoteUseCase:
    def __init__(self, lote_repo: LoteRepository, producto_repo: ProductoRepository, fermentador_repo: FermentadorRepository):
        self.lote_repo = lote_repo
        self.producto_repo = producto_repo
        self.fermentador_repo = fermentador_repo

    def execute(self, producto_nombre: str, numero: int, identificador_fermentador: int) -> dict:
        producto = self.producto_repo.get_by_nombre(producto_nombre)
        if not producto:
            raise ValueError(f"Producto '{producto_nombre}' no encontrado.")

        fermentador = self.fermentador_repo.get_by_identificador(identificador_fermentador)
        if not fermentador:
            raise ValueError(f"Fermentador '{identificador_fermentador}' no encontrado.")

        identificador_lote = f"{producto_nombre.lower()}_{numero}"

        nuevo_lote = self.lote_repo.create(
            id_producto=producto.id,
            id_fermentador=fermentador.id,
            numero=numero,
            fecha_creacion=date.today(),
            identificador_lote=identificador_lote
        )

        return {
            "mensaje": "Lote registrado exitosamente.",
            "lote": {
                "id": nuevo_lote.id,
                "identificador": nuevo_lote.identificador_lote,
                "producto": producto.nombre,
                "fermentador": fermentador.identificador_fermentador
            }
        }