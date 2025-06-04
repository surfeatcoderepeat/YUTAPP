# app/services/message_router.py

from app.services.parsers import (
    cliente,
    producto,
    botella,
    barril,
    fermentador,
    rotulo,
    registro_fermentador,
    venta,
    precio,
)

from app.services.classifier import clasificar_mensaje

PARSERS = {
    "cliente": cliente,
    "producto": producto,
    "botella": botella,
    "barril": barril,
    "fermentador": fermentador,
    "rotulo": rotulo,
    "registro_fermentador": registro_fermentador,
    "venta": venta,
    "precio": precio,
    # los operativos se agregan después
}

async def procesar_mensaje_general(mensaje: str, user: str) -> dict:
    """
    Clasifica el mensaje, selecciona el parser correspondiente y retorna el resultado.
    Si no se reconoce el tipo, devuelve el set de opciones para que el usuario elija.
    """
    print(f"[DEBUG] Clasificando mensaje: {mensaje} (usuario: {user})")
    tipo = await clasificar_mensaje(mensaje, user)
    print(f"[DEBUG] Tipo clasificado: {tipo}")

    if tipo not in PARSERS:
        return {
            "ok": False,
            "error": None,
            "mensaje": "No pude clasificar el mensaje. ¿Qué querés registrar?",
            "opciones": list(PARSERS.keys())
        }

    parser = PARSERS[tipo]
    print(f"[DEBUG] Usando parser: {parser.__name__}")
    return parser(mensaje, user)