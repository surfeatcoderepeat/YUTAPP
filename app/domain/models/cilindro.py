from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Optional

Ubicacion = Literal["fábrica", "cliente"]

@dataclass
class Cilindro:
    identificador: int  # ID físico del cilindro, número entero
    capacidad_kg: float  # Capacidad total del cilindro en kilogramos (CO₂)
    peso_vacio: float  # Peso vacío del cilindro en kilogramos
    ubicacion: Ubicacion  # "fábrica" o "cliente"
    id_cliente: Optional[int] = None  # Solo si ubicación es cliente
    porcentaje_carga: float = 0.0  # 0% a 100%
    fecha_alta: datetime = datetime.now()  # Fecha de creación del cilindro
    fecha_control: Optional[datetime] = None  # Última vez que se actualizó el estado

    def actualizar_peso(self, peso_actual: float):
        """Actualiza el porcentaje de carga en base al peso actual."""
        peso_contenido = peso_actual - self.peso_vacio
        self.porcentaje_carga = max(0.0, min(100.0, (peso_contenido / self.capacidad_kg) * 100))
        self.fecha_control = datetime.now()