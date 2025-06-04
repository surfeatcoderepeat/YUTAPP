from app.db.database import SessionLocal
from app.db.models import Fermentador

def existe_fermentador(id_fermentador: int) -> bool:
    session = SessionLocal()
    try:
        return session.query(Fermentador).filter(Fermentador.id == id_fermentador).first() is not None
    finally:
        session.close()