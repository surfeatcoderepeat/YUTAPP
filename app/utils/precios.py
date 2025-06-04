from app.db.database import SessionLocal
from app.db.models import Precio

def get_precio_producto_formato(producto_id: int, formato: str) -> float | None:
    session = SessionLocal()
    try:
        precio = (
            session.query(Precio)
            .filter(Precio.producto_id == producto_id, Precio.formato == formato)
            .order_by(Precio.vigente_desde.desc())
            .first()
        )
        return precio.precio_litro if precio else None
    finally:
        session.close()