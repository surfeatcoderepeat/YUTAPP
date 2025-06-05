from app.domain.models.cliente import Cliente
from app.infrastructure.repositories.cliente_repo import guardar_cliente
from datetime import datetime

def registrar_cliente(nombre: str, documento: str, telegram_user: str) -> str:
    nuevo_cliente = Cliente(
        nombre=nombre,
        documento=documento,
        creado_por=telegram_user,
        fecha_alta=datetime.now(datetime.timezone.utc)
    )
    guardar_cliente(nuevo_cliente)
    return f"Cliente '{nombre}' registrado correctamente."