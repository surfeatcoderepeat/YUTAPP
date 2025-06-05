

from dataclasses import dataclass
from datetime import date
from typing import Optional

@dataclass
class Rotulo:
    id: int
    producto: str  # Nombre del producto asociado
    fecha_ingreso: date
    cantidad: int
    descripcion: Optional[str] = None