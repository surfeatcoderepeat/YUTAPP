

from app.infrastructure.db.database import SessionLocal
from app.infrastructure.db.models import Lote
from sqlalchemy.orm import Session
from datetime import datetime

class LoteRepository:
    def __init__(self):
        self.db: Session = SessionLocal()

    def create_lote(self, id_fermentador: int, id_producto: int, numero: int, fecha_creacion: datetime = None):
        if fecha_creacion is None:
            fecha_creacion = datetime.now()
        identificador_lote = f"{self.get_product_name(id_producto)}_{numero}"
        nuevo_lote = Lote(
            id_fermentador=id_fermentador,
            id_producto=id_producto,
            numero=numero,
            fecha_creacion=fecha_creacion,
            identificador_lote=identificador_lote
        )
        self.db.add(nuevo_lote)
        self.db.commit()
        self.db.refresh(nuevo_lote)
        return nuevo_lote

    def get_lote_by_identificador(self, identificador_lote: str):
        return self.db.query(Lote).filter(Lote.identificador_lote == identificador_lote).first()

    def get_lote_by_id(self, id: int):
        return self.db.query(Lote).filter(Lote.id == id).first()

    def get_all_lotes(self):
        return self.db.query(Lote).all()

    def get_product_name(self, id_producto: int):
        producto = self.db.execute(
            f"SELECT nombre FROM producto WHERE id = {id_producto}"
        ).fetchone()
        return producto[0] if producto else "producto_desconocido"