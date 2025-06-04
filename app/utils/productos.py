from app.db.database import SessionLocal
from app.db.models import Producto

def get_producto_id(nombre: str) -> int | None:
    session = SessionLocal()
    try:
        producto = session.query(Producto).filter(Producto.nombre.ilike(nombre)).first()
        return producto.id if producto else None
    finally:
        session.close()


# Devuelve una lista con los nombres de todos los productos válidos
def get_productos_validos() -> list[str]:
    session = SessionLocal()
    try:
        productos = session.query(Producto).all()
        return [p.nombre for p in productos]
    finally:
        session.close()