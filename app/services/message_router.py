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
    "Registrar nuevo cliente": cliente,
    "Registrar nuevo producto": producto,
    "Registrar nuevo barril": barril,
    "Registrar nueva botella": botella,
    "Registrar nuevo fermentador": fermentador,
    "Registrar nuevo rótulo": rotulo,
    "Registrar registro fermentador": registro_fermentador,
    "Registrar despacho de cerveza": venta,  
    "Registrar retorno de botellas": botella,
    "Registrar retorno de barriles": barril,
    "Registrar venta": venta,
    "Registrar precio": precio,
}

async def procesar_mensaje_general(mensaje: str, user: str) -> dict:
    """
    Clasifica el mensaje, selecciona el parser correspondiente y retorna el resultado.
    Si no se reconoce el tipo, devuelve el set de opciones para que el usuario elija.
    """
    print(f"[DEBUG] Clasificando mensaje: {mensaje} (usuario: {user})")
    clasificacion = await clasificar_mensaje(mensaje)
    print(f"[DEBUG] Tipo clasificado: {tipo}")

    categoria = clasificacion.get("categoria", "desconocido")

    if categoria not in PARSERS:
        return {
            "ok": False,
            "error": None,
            "mensaje": "No pude clasificar el mensaje. ¿Qué querés registrar?",
            "opciones": list(PARSERS.keys())
        }

    parser = PARSERS[categoria]
    print(f"[DEBUG] Usando parser: {parser.__name__}")
    return parser(mensaje, user)