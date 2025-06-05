from pydantic import BaseModel, Field
from datetime import datetime

class Cliente(BaseModel):
    id: int | None = Field(default=None, description="ID interno autoincremental")
    nombre: str = Field(..., description="Nombre del cliente")
    cnpj_cpf: str = Field(..., description="Documento de identificación fiscal (CNPJ o CPF)")
    fecha_alta: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación del cliente")
