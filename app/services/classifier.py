# app/services/classifier.py

from typing import Optional

TIPOS_ENTIDAD = {
    "cliente": ["cliente", "registrar cliente", "nuevo cliente"],
    "barril": ["barril", "nuevo barril", "ingresó el barril"],
    "movimiento_stock": ["salieron", "movimiento de stock", "entraron", "salida de stock"],
    "venta": ["vendimos", "venta", "pedido", "cobramos"],
    "precio": ["precio por litro", "precio"],
    "fermentador": ["fermentador", "llenado de fermentador", "número de fermentador"],
    "reporte_fermentador": ["fermentación", "reporte de fermentador", "estado del fermentador"],
    "muestra": ["muestra tomada", "densidad", "antes de adicionar", "lote"],
    "movimiento_botella": ["botellas", "botellas recicladas", "ingresaron botellas"],
    "movimiento_rotulo": ["rótulos", "etiquetas", "rotulo", "se usaron"],
    "movimiento_barril": ["barril volvió", "barril devuelto", "vacío del cliente"]
}

def clasificar_mensaje(mensaje: str) -> Optional[str]:
    mensaje = mensaje.lower()
    for tipo, patrones in TIPOS_ENTIDAD.items():
        if any(p in mensaje for p in patrones):
            return tipo
    return None