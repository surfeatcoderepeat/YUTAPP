# app/services/message_router.py

from app.interfaces.parsers import (
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

from app.infrastructure.openai.classifier import clasificar_mensaje

import json

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

async def procesar_mensaje_general(mensaje: str, user: str) -> dict:
    print(f"[DEBUG][router] Clasificando mensaje: {mensaje} (usuario: {user})")

    clasificacion = await clasificar_mensaje(mensaje)

    try:
        raw = clasificacion.get("respuesta", None)
        print(f"[DEBUG][router] Respuesta bruta de OpenAI: {raw} (tipo: {type(raw)})")

        if isinstance(raw, str):
            categorias = json.loads(raw)
        elif isinstance(raw, list):
            categorias = raw
        else:
            print(f"[ERROR][router] Tipo inesperado de respuesta: {type(raw)}")
            categorias = []

    except Exception as e:
        print(f"[ERROR][router] No se pudo parsear la respuesta de OpenAI: {e}")
        categorias = []

    print(f"[DEBUG][router] Categorías detectadas: {categorias}")

    if not categorias:
        return {
            "ok": False,
            "mensaje": "No pude clasificar el mensaje. ¿Qué querés registrar?",
            "opciones": list(PARSERS.keys())
        }

    errores = []
    resultados = []
    for categoria in categorias:
        parser = PARSERS.get(categoria)
        if parser:
            print(f"[DEBUG][router] Usando parser para '{categoria}': {parser.__name__}")
            resultado = await parser(mensaje, user)
            if resultado.get("ok"):
                resultados.append((categoria, resultado))
            else:
                errores.append({
                    "categoria": categoria,
                    "mensaje": resultado.get("mensaje", "Fallo sin mensaje.")
                })
                print(f"[ERROR][router] Falló parser para '{categoria}': {resultado.get('mensaje')}")

    if not resultados:
        return {
            "ok": False,
            "mensaje": "No se pudo procesar ninguna acción.",
            "errores": errores,
            "categorias": categorias
        }

    if len(resultados) == 1:
        categoria, resultado = resultados[0]
        resultado["mensaje_usuario"] = f"✅ Acción registrada como: {categoria}"
        return resultado

    datos_combinados = {}
    for categoria, resultado in resultados:
        if "datos" in resultado:
            datos_combinados[categoria] = resultado["datos"]

    return {
        "ok": True,
        "tabla_destino": "multiple",
        "datos": datos_combinados,
        "mensaje_usuario": "✅ Se procesaron múltiples acciones."
    }