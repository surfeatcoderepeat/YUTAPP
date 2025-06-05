

from datetime import datetime
from pydantic import BaseModel, Field

class Fermentador(BaseModel):
    identificador: int = Field(..., description="Identificador físico del fermentador (1-7)")
    capacidad_litros: float = Field(..., description="Capacidad total en litros del fermentador")
    estado_actual: str = Field(default="vacío", description="Estado actual del fermentador (vacío, en uso, etc.)")
    fecha_alta: datetime = Field(default_factory=datetime.utcnow, description="Fecha de alta del fermentador")