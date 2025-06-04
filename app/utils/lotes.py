from app.db.database import SessionLocal
from app.db.models import Lote
from datetime import datetime

def get_lote_id(lote_descripcion: str, producto_id: int) -> int | None:
    """Devuelve el ID del lote si existe, o None si no."""
    session = SessionLocal()
    try:
        lote = session.query(Lote).filter_by(descripcion=lote_descripcion).first()
        return lote.id if lote else None
    finally:
        session.close()


def existe_lote_id(lote_id: int) -> bool:
    session = SessionLocal()
    try:
        return session.query(Lote).filter(Lote.id == lote_id).first() is not None
    finally:
        session.close()

def crear_lote_si_no_existe(descripcion: str, id_fermentador: int | None = None) -> int:
    """
    Si el lote no existe, lo crea y devuelve su ID. Si existe, devuelve su ID actual.
    """
    session = SessionLocal()
    try:
        lote = session.query(Lote).filter_by(descripcion=descripcion).first()
        if lote:
            return lote.id

        nuevo_lote = Lote(
            descripcion=descripcion,
            id_fermentador=id_fermentador,
            fecha_creacion=datetime.now()
        )
        session.add(nuevo_lote)
        session.commit()
        return nuevo_lote.id
    finally:
        session.close()