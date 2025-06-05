

from sqlalchemy.orm import Session
from app.infrastructure.db.models import Precio
from datetime import datetime


def create_precio(db: Session, producto_id: int, formato: str, precio: float) -> Precio:
    nuevo_precio = Precio(
        producto_id=producto_id,
        formato=formato,
        precio=precio,
        fecha_creacion=datetime.now()
    )
    db.add(nuevo_precio)
    db.commit()
    db.refresh(nuevo_precio)
    return nuevo_precio


def get_precios_por_producto(db: Session, producto_id: int) -> list[Precio]:
    return db.query(Precio).filter(Precio.producto_id == producto_id).all()


def get_precio_actual(db: Session, producto_id: int, formato: str) -> Precio:
    return (
        db.query(Precio)
        .filter(Precio.producto_id == producto_id, Precio.formato == formato)
        .order_by(Precio.fecha_creacion.desc())
        .first()
    )