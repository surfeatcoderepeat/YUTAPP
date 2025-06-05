from app.infrastructure.openai.client import openai_client
from app.application.use_cases.registrar_cilindro import registrar_cilindro
from app.infrastructure.repositories.cilindro_repo import CilindroRepository

def parse_registrar_cilindro(message: str, sender: str) -> str:
    prompt = f"""
    Extraé los siguientes campos del mensaje y devolvelos en formato JSON:
    - identificador_cilindro: identificador físico del cilindro (int).
    - capacidad: capacidad en kilogramos del cilindro (float).
    - peso_vacio: peso vacío del cilindro en kilogramos (float).
    - ubicacion: ubicación actual del cilindro ('fábrica' o 'cliente').
    - porcentaje_carga (opcional): porcentaje de carga actual (float).
    - id_cliente (opcional): ID del cliente si la ubicación es 'cliente' (int).

    Mensaje: \"{message}\"
    """
    response = openai_client(prompt)
    fields = response.get("fields", {})

    required_fields = ["identificador_cilindro", "capacidad", "peso_vacio", "ubicacion"]
    if not all(k in fields and fields[k] is not None for k in required_fields):
        return "Faltan datos obligatorios para registrar el cilindro."

    repo = CilindroRepository()
    return registrar_cilindro(fields, repo)