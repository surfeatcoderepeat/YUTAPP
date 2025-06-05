

from app.domain.models.precio import Precio
from app.infrastructure.repositories.precio_repo import PrecioRepository
from datetime import date

def registrar_precio(nombre_producto: str, formato: str, valor: float, fecha: date = None):
    repo = PrecioRepository()
    if fecha is None:
        fecha = date.today()

    if not repo.producto_existe(nombre_producto):
        raise ValueError(f"Producto '{nombre_producto}' no existe.")

    nuevo_precio = Precio(
        nombre_producto=nombre_producto,
        formato=formato,
        valor=valor,
        fecha_creacion=fecha
    )

    repo.guardar_precio(nuevo_precio)
    return f"Precio de {valor} para {nombre_producto} en formato {formato} registrado con fecha {fecha}."