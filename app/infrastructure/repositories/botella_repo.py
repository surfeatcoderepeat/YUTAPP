

from sqlalchemy.orm import Session
from app.domain.models.botella import Botella

def crear_botella(db: Session, botella_data: dict) -> Botella:
    nueva_botella = Botella(**botella_data)
    db.add(nueva_botella)
    db.commit()
    db.refresh(nueva_botella)
    return nueva_botella

def obtener_botella_por_producto_y_lote(db: Session, id_producto: int, id_lote: int):
    return db.query(Botella).filter(
        Botella.id_producto == id_producto,
        Botella.id_lote == id_lote
    ).first()

def actualizar_botella(db: Session, botella: Botella, datos_actualizados: dict) -> Botella:
    for campo, valor in datos_actualizados.items():
        setattr(botella, campo, valor)
    db.commit()
    db.refresh(botella)
    return botella