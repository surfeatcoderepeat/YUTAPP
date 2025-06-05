from sqlalchemy.orm import Session
from app.domain.models.barril import Barril


def get_barril_by_identificador(db: Session, identificador_barril: str) -> Barril | None:
    return db.query(Barril).filter(Barril.identificador_barril == identificador_barril).first()


def create_barril(db: Session, barril_data: dict) -> Barril:
    nuevo_barril = Barril(**barril_data)
    db.add(nuevo_barril)
    db.commit()
    db.refresh(nuevo_barril)
    return nuevo_barril


# Nueva función para actualizar campos de un barril existente
def update_barril(db: Session, identificador_barril: str, update_data: dict) -> Barril | None:
    barril = db.query(Barril).filter(Barril.identificador_barril == identificador_barril).first()
    if barril is None:
        return None
    for key, value in update_data.items():
        setattr(barril, key, value)
    db.commit()
    db.refresh(barril)
    return barril