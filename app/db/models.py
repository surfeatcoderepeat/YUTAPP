from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Cliente(Base):
    """Representa a un cliente que recibe productos."""
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    cnpj_cpf = Column(String, nullable=True)


class Envase(Base):
    """Representa un tipo de envase (botella, barril) con volumen definido."""
    __tablename__ = "envases"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)  # barril o botella
    volumen_litros = Column(Float, nullable=False)
    reutilizable = Column(Boolean, default=False)


class MovimientoStock(Base):
    """Registro de entrada o salida de stock, asociado a producto, cliente y envase."""
    __tablename__ = "movimientos_stock"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)  # entrada o salida
    producto = Column(String, nullable=False)
    lote = Column(Integer, nullable=False)
    volumen_litros = Column(Float, nullable=False)
    formato = Column(String, nullable=False)  # botella o barril
    id_envase = Column(Integer, ForeignKey("envases.id"), nullable=True)
    id_cliente = Column(Integer, ForeignKey("clientes.id"), nullable=True)
    responsable = Column(String, nullable=False)
    observacion = Column(String, nullable=True)
    mensaje_original = Column(String, nullable=False)

    cliente = relationship("Cliente")
    envase = relationship("Envase")


class Barril(Base):
    """Barril individual identificado por ID y asociado a un lote."""
    __tablename__ = "barriles"

    id = Column(Integer, primary_key=True, index=True)
    volumen_litros = Column(Float, nullable=False)
    producto = Column(String, nullable=False)
    lote = Column(Integer, nullable=False)
    estado = Column(String, nullable=False)  # lleno, vacío, limpio, sucio
    ubicacion = Column(String, nullable=False)  # fábrica, cliente, etc.


class MovimientoEnvases(Base):
    """Movimiento de botellas o rótulos, para reciclado, embotellado o descarte."""
    __tablename__ = "movimientos_envases"

    id = Column(Integer, primary_key=True, index=True)
    tipo = Column(String, nullable=False)  # botella, rótulo
    accion = Column(String, nullable=False)  # reciclado, embotellado, etc.
    cantidad = Column(Integer, nullable=False)
    producto = Column(String, nullable=True)
    fecha = Column(DateTime, nullable=False)
    responsable = Column(String, nullable=False)


class Precio(Base):
    """Precio por litro por producto y formato."""
    __tablename__ = "precios"

    id = Column(Integer, primary_key=True, index=True)
    producto = Column(String, nullable=False)
    formato = Column(String, nullable=False)
    precio_litro = Column(Float, nullable=False)
    vigente_desde = Column(DateTime, nullable=False)


class Venta(Base):
    """Registro de venta de cerveza a un cliente."""
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    fecha_pedido = Column(DateTime, nullable=False)
    fecha_cobro = Column(DateTime, nullable=True)
    producto = Column(String, nullable=False)
    formato = Column(String, nullable=False)
    volumen_litros = Column(Float, nullable=False)
    cantidad = Column(Integer, nullable=False)
    id_cliente = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    responsable = Column(String, nullable=False)
    precio_unitario = Column(Float, nullable=False)
    precio_total = Column(Float, nullable=False)

    cliente = relationship("Cliente")


class Fermentador(Base):
    """Registro de fermentadores con capacidad y estado."""
    __tablename__ = "fermentadores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    capacidad_litros = Column(Float, nullable=False)
    estado_actual = Column(String, nullable=False)


class Lote(Base):
    """Representa un lote de cerveza asociado a un fermentador."""
    __tablename__ = "lotes"

    id = Column(Integer, primary_key=True, index=True)
    id_fermentador = Column(Integer, ForeignKey("fermentadores.id"), nullable=False)
    producto = Column(String, nullable=False)
    fecha_inicio = Column(DateTime, nullable=False)
    fecha_embarrilado = Column(DateTime, nullable=True)
    observaciones = Column(String, nullable=True)

    fermentador = relationship("Fermentador")


class ReporteFermentador(Base):
    """Entradas de seguimiento del estado de un fermentador durante un lote."""
    __tablename__ = "reportes_fermentador"

    id = Column(Integer, primary_key=True, index=True)
    id_lote = Column(Integer, ForeignKey("lotes.id"), nullable=False)
    fecha = Column(DateTime, nullable=False)
    responsable = Column(String, nullable=False)
    etapa = Column(String, nullable=False)  # fermentación, maduración, etc.
    observaciones = Column(String, nullable=True)

    lote = relationship("Lote")