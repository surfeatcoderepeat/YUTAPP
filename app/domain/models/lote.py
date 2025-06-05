

from datetime import date
from pydantic import BaseModel
from typing import Optional

class Lote(BaseModel):
    id: Optional[int]
    identificador_lote: str
    id_producto: int
    id_fermentador: int
    fecha_creacion: date