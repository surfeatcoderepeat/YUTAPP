from dataclasses import dataclass
from datetime import datetime
from typing import Optional

# Botellas se manejan por lote y producto, no individualmente
@dataclass
class Botella:
    capacidad_litros: float
    cantidad: int
    estado: str  # 'vacías', 'llenas', 'en limpieza', etc.
    ubicacion: str  # 'fábrica' o nombre del cliente
    id_producto: Optional[int] = None
    id_lote: Optional[int] = None
    fecha_alta: datetime = datetime.now()
    fecha_control: Optional[datetime] = None