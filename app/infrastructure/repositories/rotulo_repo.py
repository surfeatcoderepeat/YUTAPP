

from app.infrastructure.db.database import SessionLocal
from app.infrastructure.db.models import Rotulo
from sqlalchemy.orm import Session
from typing import Optional


class RotuloRepository:

    def __init__(self, db: Optional[Session] = None):
        self.db = db or SessionLocal()

    def get_stock_by_producto(self, producto_id: int) -> Optional[Rotulo]:
        return (
            self.db.query(Rotulo)
            .filter(Rotulo.id_producto == producto_id)
            .first()
        )

    def ingresar_rotulos(self, producto_id: int, cantidad: int):
        rotulo = self.get_stock_by_producto(producto_id)
        if rotulo:
            rotulo.stock += cantidad
        else:
            rotulo = Rotulo(id_producto=producto_id, stock=cantidad)
            self.db.add(rotulo)
        self.db.commit()
        self.db.refresh(rotulo)
        return rotulo

    def consumir_rotulos(self, producto_id: int, cantidad: int) -> bool:
        rotulo = self.get_stock_by_producto(producto_id)
        if rotulo and rotulo.stock >= cantidad:
            rotulo.stock -= cantidad
            self.db.commit()
            return True
        return False