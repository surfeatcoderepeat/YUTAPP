from app.db.database import SessionLocal
from app.db.models import Producto

def get_producto_id(nombre: str) -> int | None:
    session = SessionLocal()
    try:
        producto = session.query(Producto).filter(Producto.nombre.ilike(nombre)).first()
        return producto.id if producto else None
    finally:
        session.close()