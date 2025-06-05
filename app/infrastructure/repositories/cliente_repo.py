

from sqlalchemy.orm import Session
from app.infrastructure.db.models import Cliente

def crear_cliente(db: Session, nombre: str, identificador: str):
    cliente_existente = db.query(Cliente).filter(Cliente.identificador == identificador).first()
    if cliente_existente:
        return cliente_existente
    nuevo_cliente = Cliente(nombre=nombre, identificador=identificador)
    db.add(nuevo_cliente)
    db.commit()
    db.refresh(nuevo_cliente)
    return nuevo_cliente

def obtener_cliente_por_identificador(db: Session, identificador: str):
    return db.query(Cliente).filter(Cliente.identificador == identificador).first()

def listar_clientes(db: Session):
    return db.query(Cliente).order_by(Cliente.nombre).all()