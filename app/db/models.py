# app/db/models.py
from sqlalchemy import Column, Integer, String, DateTime, Float, Text
from datetime import datetime
from app.db.database import Base

class MovimientoStock(Base):
    __tablename__ = "movimientos_stock"

    id = Column(Integer, primary_key=True, index=True)

    fecha = Column(DateTime, default=datetime.utcnow, nullable=False)
    tipo = Column(String(20), nullable=False)                   # 'salida', 'entrada', etc.
    producto = Column(String(100), nullable=False)          # IPA PILSEN ETC
    formato = Column(String(20), nullable=False)                # 'barril', 'botella', etc.
    volumen_litros = Column(Float, nullable=False)
    lote = Column(String(50), nullable=False)

    cliente = Column(String(100), nullable=False)
    responsable = Column(String(100), nullable=False)

    id_barril = Column(Integer, nullable=True)                  # Solo si formato == 'barril'
    observacion = Column(Text, nullable=True)                   # Libre

    mensaje_original = Column(Text, nullable=False)             # Texto crudo recibido