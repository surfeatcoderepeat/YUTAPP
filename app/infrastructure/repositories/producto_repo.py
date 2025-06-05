from app.infrastructure.db.base import get_db
from app.infrastructure.db.models import Producto
from .producto_repo import create_producto, get_producto_by_nombre
from sqlalchemy.orm import Session

class ProductoRepository:
    def __init__(self, db: Session = None):
        self.db = db or get_db()

    def exists(self, nombre: str) -> bool:
        return get_producto_by_nombre(self.db, nombre) is not None

    def add(self, producto: Producto) -> None:
        create_producto(self.db, producto.nombre, producto.descripcion)