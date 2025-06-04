from app.db.database import SessionLocal
from app.db.models import Lote

def get_lote_id(lote_nombre: str, producto_id: int) -> int | None:
    """Devuelve el ID del lote si existe, o None si no."""
    session = SessionLocal()
    try:
        lote = session.query(Lote).filter_by(nombre=lote_nombre, id_producto=producto_id).first()
        return lote.id if lote else None
    finally:
        session.close()


def existe_lote_id(lote_id: int) -> bool:
    session = SessionLocal()
    try:
        return session.query(Lote).filter(Lote.id == lote_id).first() is not None
    finally:
        session.close()