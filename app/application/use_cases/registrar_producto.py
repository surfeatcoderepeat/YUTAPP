

from app.domain.models.producto import Producto
from app.infrastructure.repositories.producto_repo import ProductoRepository

class RegistrarProductoUseCase:
    def __init__(self, producto_repo: ProductoRepository):
        self.producto_repo = producto_repo

    def execute(self, nombre: str, descripcion: str = ""):
        if self.producto_repo.exists(nombre):
            return f"Ya existe un producto con el nombre '{nombre}'."

        nuevo_producto = Producto(nombre=nombre, descripcion=descripcion)
        self.producto_repo.add(nuevo_producto)

        return f"Producto '{nombre}' registrado correctamente."