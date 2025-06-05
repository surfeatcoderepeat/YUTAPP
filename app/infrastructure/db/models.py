# Importar todos los modelos explícitamente para que Alembic los detecte en Base.metadata

from app.domain.models.barril import Barril
from app.domain.models.botella import Botella
from app.domain.models.cilindro import Cilindro
from app.domain.models.cliente import Cliente
from app.domain.models.fermentador import Fermentador
from app.domain.models.lote import Lote
from app.domain.models.precio import Precio
from app.domain.models.producto import Producto
from app.domain.models.rotulo import Rotulo
from app.infrastructure.db.base import Base

metadata = Base.metadata