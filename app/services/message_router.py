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
    "Registrar nuevo cliente": cliente.parse_cliente,
    "Registrar nuevo producto": producto.parse_producto,
    "Registrar nuevo barril": barril.parse_barril,
    "Registrar nueva botella": botella.parse_botella,
    "Registrar nuevo fermentador": fermentador.parse_fermentador,
    "Registrar nuevo rótulo": rotulo.parse_rotulo,
    "Registrar registro fermentador": registro_fermentador.parse_registro_fermentador,
    "Registrar despacho de cerveza": barril.parse_barril,  
    "Registrar retorno de botellas": botella.parse_botella,
    "Registrar retorno de barriles": barril.parse_barril,
    "Registrar venta": venta.parse_venta,
    "Registrar precio": precio.parse_precio,
}

async def procesar_mensaje_general(mensaje: str, user: str, forzar_clasificacion: str = None) -> dict:
    """
    Clasifica el mensaje, selecciona el parser correspondiente y retorna el resultado.
    Si no se reconoce el tipo, devuelve el set de opciones para que el usuario elija.
    """
    print(f"[DEBUG] Clasificando mensaje: {mensaje} (usuario: {user})")
    if forzar_clasificacion:
        clasificacion = {"ok": True, "categoria": forzar_clasificacion}
        print(f"[DEBUG] Clasificación forzada: {clasificacion}")
    else:
        clasificacion = await clasificar_mensaje(mensaje)
    print(f"[DEBUG] Tipo clasificado: {clasificacion}")

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
    return await parser(mensaje, user)