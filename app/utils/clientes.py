from app.db.database import SessionLocal
from app.db.models import Cliente

def get_cliente_id_por_nombre(nombre: str) -> int | None:
    session = SessionLocal()
    try:
        cliente = session.query(Cliente).filter(Cliente.nombre.ilike(nombre)).first()
        return cliente.id if cliente else None
    finally:
        session.close()