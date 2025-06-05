from dataclasses import dataclass
from typing import Optional
from uuid import UUID
from datetime import datetime

@dataclass
class Barril:
    id: UUID
    identificador_barril: str  # ID físico del barril (etiqueta)
    volumen_litros: float
    estado: str  # Ej: "lleno", "vacío", "en limpieza", etc.
    ubicacion: str  # Ej: "fábrica", "cliente", etc.
    id_producto: Optional[UUID] = None
    id_lote: Optional[UUID] = None
    fecha_creacion: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
