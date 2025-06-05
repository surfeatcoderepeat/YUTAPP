from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.infrastructure.db.base import Base

class Producto(Base):
    __tablename__ = 'productos'

    id = Column(Integer, primary_key=True)
    nombre = Column(String, unique=True, nullable=False)
    descripcion = Column(String, nullable=True)
    fecha_creacion = Column(DateTime, default=lambda: datetime.now(datetime.timezone.utc))