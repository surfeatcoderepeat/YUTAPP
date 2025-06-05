

from app.infrastructure.db.database import Session
from app.infrastructure.db.models import Fermentador

def create_fermentador(db: Session, identificador_fermentador: int, capacidad_litros: float, estado_actual: str):
    fermentador = Fermentador(
        identificador_fermentador=identificador_fermentador,
        capacidad_litros=capacidad_litros,
        estado_actual=estado_actual
    )
    db.add(fermentador)
    db.commit()
    db.refresh(fermentador)
    return fermentador

def get_fermentador_by_identificador(db: Session, identificador_fermentador: int):
    return db.query(Fermentador).filter(Fermentador.identificador_fermentador == identificador_fermentador).first()

def get_all_fermentadores(db: Session):
    return db.query(Fermentador).all()

def update_estado_fermentador(db: Session, identificador_fermentador: int, nuevo_estado: str):
    fermentador = get_fermentador_by_identificador(db, identificador_fermentador)
    if fermentador:
        fermentador.estado_actual = nuevo_estado
        db.commit()
        db.refresh(fermentador)
    return fermentador