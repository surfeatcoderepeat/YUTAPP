# app/services/telegram_bot.py
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from app.core.config import get_settings
from app.services.message_router import procesar_mensaje_general
from app.db.database import SessionLocal
from app.db import models
import asyncio

# Cargar configuración con manejo de errores
try:
    settings = get_settings()
except Exception as e:
    print(f"❌ Error al cargar configuración: {e}")
    settings = None

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user.first_name or "usuario"
    chat_id = update.effective_chat.id
    message_text = update.message.text

    await context.bot.send_message(chat_id=chat_id, text=f"📩 Recibido, {user}. Procesando tu mensaje...")

    resultado = await procesar_mensaje_general(message_text, user)

    if not resultado["ok"]:
        if "error" in resultado:
            await context.bot.send_message(chat_id=chat_id, text=f"❌ Error: {resultado['error']}")
        else:
            campos = ", ".join(resultado["faltantes"])
            await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Faltan datos: {campos}. ¿Podés completar?")
        return

    datos = resultado["datos"]

    # Guardar datos en la base de datos
    tabla_destino = resultado.get("tabla_destino")
    session = SessionLocal()
    try:
        modelo = getattr(models, tabla_destino, None)
        if modelo is None:
            await context.bot.send_message(chat_id=chat_id, text=f"❌ Error: La tabla '{tabla_destino}' no existe.")
            return
        instancia = modelo(**datos)
        session.add(instancia)
        session.commit()
    except Exception as e:
        session.rollback()
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Error al guardar en la base de datos: {e}")
        return
    finally:
        session.close()

    # Mensaje de confirmación dinámico
    texto_confirmacion = "\n".join(
        [f"- {k.replace('_', ' ').capitalize()}: {v}" for k, v in datos.items() if k != "mensaje_original"]
    )

    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ Registro exitoso:\n{texto_confirmacion}"
    )

async def start_bot():
    if not settings:
        print("🚫 Bot no iniciado: configuración inválida.")
        return

    try:
        application = ApplicationBuilder().token(settings.telegram_bot_token).build()
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        print("🤖 Bot iniciado y escuchando mensajes...")

        await application.initialize()
        await application.start()
        await application.updater.start_polling()

    except Exception as e:
        print(f"❌ Error al iniciar el bot: {e}")