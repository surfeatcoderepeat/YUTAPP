

from sqlalchemy.orm import Session
from app.infrastructure.db import models

def create_cilindro(db: Session, identificador: str, capacidad_kg: float):
    cilindro = models.Cilindro(
        identificador_cilindro=identificador,
        capacidad_kg=capacidad_kg,
        estado="disponible",
        peso_actual_kg=0.0,
        ubicacion="fábrica"
    )
    db.add(cilindro)
    db.commit()
    db.refresh(cilindro)
    return cilindro

def get_cilindro_by_identificador(db: Session, identificador: str):
    return db.query(models.Cilindro).filter(models.Cilindro.identificador_cilindro == identificador).first()

def update_cilindro(db: Session, identificador: str, updates: dict):
    cilindro = get_cilindro_by_identificador(db, identificador)
    if not cilindro:
        return None
    for key, value in updates.items():
        setattr(cilindro, key, value)
    db.commit()
    db.refresh(cilindro)
    return cilindro

def list_cilindros(db: Session):
    return db.query(models.Cilindro).all()