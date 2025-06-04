from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.db.database import Base

class Cliente(Base):
    """Representa a un cliente que recibe productos."""
    __tablename__ = "clientes"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    cnpj_cpf = Column(String, nullable=True)


class Producto(Base):
    """Estilo o tipo de cerveza producida."""
    __tablename__ = "productos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False, unique=True)
    descripcion = Column(String, nullable=True)


class Botella(Base):
    """Registro de botellas por tipo de capacidad y estado."""
    __tablename__ = "botellas"

    id = Column(Integer, primary_key=True, index=True)
    estado = Column(String, nullable=False)  # disponible, sucia, en uso
    ubicacion = Column(String, nullable=False)  # fábrica, cliente, etc.
    id_lote = Column(Integer, ForeignKey("lotes.id"), nullable=True)
    volumen_litros = Column(Float, nullable=False)
    id_producto = Column(Integer, ForeignKey("productos.id"), nullable=False)
    lote = relationship("Lote")
    producto = relationship("Producto")


class Barril(Base):
    """Barril individual identificado por ID y su trazabilidad."""
    __tablename__ = "barriles"

    id = Column(Integer, primary_key=True, index=True)
    volumen_litros = Column(Float, nullable=False)
    id_producto = Column(Integer, ForeignKey("productos.id"), nullable=False)
    producto = relationship("Producto")
    id_lote = Column(Integer, ForeignKey("lotes.id"), nullable=True)
    lote = relationship("Lote")
    estado = Column(String, nullable=False)  # lleno, vacío, limpio, sucio
    ubicacion = Column(String, nullable=False)  # fábrica, cliente, etc.


class Fermentador(Base):
    """Fermentador disponible en la fábrica."""
    __tablename__ = "fermentadores"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, nullable=False)
    capacidad_litros = Column(Float, nullable=False)
    estado_actual = Column(String, nullable=False)


class Rotulo(Base):
    """Rótulos disponibles para embotellar según el producto."""
    __tablename__ = "rotulos"

    id = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("productos.id"), nullable=False)
    producto = relationship("Producto")
    cantidad = Column(Integer, nullable=False)


class Precio(Base):
    """Precio por litro por producto y formato."""
    __tablename__ = "precios"

    id = Column(Integer, primary_key=True, index=True)
    id_producto = Column(Integer, ForeignKey("productos.id"), nullable=False)
    formato = Column(String, nullable=False)  # botella o barril
    precio_litro = Column(Float, nullable=False)
    vigente_desde = Column(DateTime, nullable=False)

    producto = relationship("Producto")


class Venta(Base):
    """Registro de pedidos de clientes, con seguimiento completo."""
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    fecha_pedido = Column(DateTime, nullable=False)
    fecha_cobro = Column(DateTime, nullable=True)
    fecha_entrega = Column(DateTime, nullable=True)
    id_cliente = Column(Integer, ForeignKey("clientes.id"), nullable=False)
    id_producto = Column(Integer, ForeignKey("productos.id"), nullable=False)
    producto = relationship("Producto")
    formato = Column(String, nullable=False)  # botella o barril
    volumen_litros = Column(Float, nullable=False)
    cantidad = Column(Integer, nullable=False)
    ids_barriles = Column(String, nullable=True)  # para trazabilidad si aplica
    estado = Column(String, nullable=False, default="pendiente")
    observacion = Column(String, nullable=True)
    responsable = Column(String, nullable=False)

    cliente = relationship("Cliente")

class Lote(Base):
    __tablename__ = "lotes"

    id = Column(Integer, primary_key=True, index=True)
    id_fermentador = Column(Integer, ForeignKey("fermentadores.id"), nullable=False)
    fecha_creacion = Column(DateTime, nullable=False)
    descripcion = Column(String, nullable=True)

    fermentador = relationship("Fermentador")

class RegistroFermentador(Base):
    """Entradas de seguimiento del estado y eventos de un fermentador."""
    __tablename__ = "registro_fermentador"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(DateTime, nullable=False)
    id_lote = Column(Integer, ForeignKey("lotes.id"), nullable=True)
    lote = relationship("Lote")
    id_fermentador = Column(Integer, ForeignKey("fermentadores.id"), nullable=False)
    tipo_evento = Column(String, nullable=False)  # llenado, adición, muestra, embarrilado, limpieza
    descripcion = Column(String, nullable=True)
    responsable = Column(String, nullable=False)
    id_producto = Column(Integer, ForeignKey("productos.id"), nullable=False)
    producto = relationship("Producto")
    fermentador = relationship("Fermentador")