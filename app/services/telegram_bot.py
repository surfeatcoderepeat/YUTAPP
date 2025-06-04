# app/services/telegram_bot.py
from telegram import Update, ReplyKeyboardMarkup
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

# Diccionario de contexto por usuario para manejar clasificación manual
USER_CONTEXT = {}

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
            # Guardar mensaje pendiente para clasificación manual
            USER_CONTEXT[chat_id] = {"mensaje_original": message_text}
            opciones = [
                "Registrar cliente", "Registrar producto", "Registrar botella",
                "Registrar barril", "Registrar fermentador", "Registrar rótulo",
                "Registrar venta", "Registrar intervención en fermentador", "Registrar precio"
            ]
            keyboard = [[opcion] for opcion in opciones]
            reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

            await context.bot.send_message(
                chat_id=chat_id,
                text="🤔 No pude clasificar el mensaje. ¿Qué acción querés registrar?",
                reply_markup=reply_markup
            )
        return

    datos = resultado["datos"]
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

    texto_confirmacion = "\n".join(
        [f"- {k.replace('_', ' ').capitalize()}: {v}" for k, v in datos.items() if k != "mensaje_original"]
    )
    await context.bot.send_message(
        chat_id=chat_id,
        text=f"✅ Registro exitoso:\n{texto_confirmacion}"
    )

async def handle_clasificacion_manual(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    seleccion = update.message.text

    if chat_id not in USER_CONTEXT:
        await context.bot.send_message(chat_id=chat_id, text="❌ No tengo un mensaje pendiente para clasificar.")
        return

    mensaje_original = USER_CONTEXT.pop(chat_id)["mensaje_original"]

    resultado = await procesar_mensaje_general(mensaje_original, user=update.effective_user.first_name, forzar_clasificacion=seleccion)

    if not resultado["ok"]:
        await context.bot.send_message(chat_id=chat_id, text=f"❌ Error al procesar: {resultado.get('error', 'Datos incompletos')}")
        return

    datos = resultado["datos"]
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
        application.add_handler(
            MessageHandler(
                filters.TEXT & (~filters.COMMAND),
                lambda u, c: handle_clasificacion_manual(u, c) if u.effective_chat.id in USER_CONTEXT else handle_message(u, c)
            )
        )
        print("🤖 Bot iniciado y escuchando mensajes...")

        await application.run_polling()

    except Exception as e:
        print(f"❌ Error al iniciar el bot: {e}")