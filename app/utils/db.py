from app.db.database import SessionLocal
from app.db import models

async def guardar_en_base_de_datos(tabla_destino, datos, chat_id=None, context=None):

    session = SessionLocal()
    try:
        modelo = getattr(models, tabla_destino, None)
        if modelo is None:
            if context and chat_id:
                await context.bot.send_message(chat_id=chat_id, text=f"❌ Error: La tabla '{tabla_destino}' no existe.")
            return False
        if isinstance(datos, list):
            for d in datos:
                session.add(modelo(**d))
        else:
            session.add(modelo(**datos))
        session.commit()
        return True
    except Exception as e:
        session.rollback()
        if context and chat_id:
            await context.bot.send_message(chat_id=chat_id, text=f"❌ Error al guardar en la base de datos: {e}")
        return False
    finally:
        session.close()