from app.db.database import SessionLocal
from app.db.models import Lote

def existe_lote(id_lote: int) -> bool:
    session = SessionLocal()
    try:
        return session.query(Lote).filter(Lote.id == id_lote).first() is not None
    finally:
        session.close()