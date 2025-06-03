# app/services/message_router.py
from app.services.parsers import (
    parse_movimiento_stock,
    parse_venta,
    parse_cliente,
    parse_barril,
    parse_precio,
    parse_fermentador,
    parse_reporte_fermentador,
    parse_muestra,
    parse_movimiento_botella,
    parse_movimiento_rotulo,
    parse_movimiento_barril,
)

from app.services.classifier import clasificar_mensaje

from app.services.classifier import clasificar_mensaje

PARSERS = {
    "movimiento_stock": parse_movimiento_stock,
    "venta": parse_venta,
    "cliente": parse_cliente,
    "barril": parse_barril,
    "precio": parse_precio,
    "fermentador": parse_fermentador,
    "reporte_fermentador": parse_reporte_fermentador,
    "muestra": parse_muestra,
    "movimiento_botella": parse_movimiento_botella,
    "movimiento_rotulo": parse_movimiento_rotulo,
    "movimiento_barril": parse_movimiento_barril,
}

def procesar_mensaje_general(mensaje: str, user: str) -> dict:
    """
    Clasifica el mensaje, selecciona el parser correspondiente y retorna el resultado.
    """
    tipo = clasificar_mensaje(mensaje)
    
    if tipo not in PARSERS:
        return {"ok": False, "error": f"Tipo de mensaje no reconocido: {tipo}"}

    parser = PARSERS[tipo]
    return parser(mensaje, user)
