from dataclasses import dataclass
from datetime import date

@dataclass
class Precio:
    producto: str
    formato: str  # por ejemplo, "barril", "botella"
    precio_unitario: float
    fecha_creacion: date
