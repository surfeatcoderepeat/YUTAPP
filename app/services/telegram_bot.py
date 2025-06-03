# app/services/telegram_bot.py
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from app.core.config import get_settings
from app.services.gpt_parser import interpretar_mensaje
from app.db.database import SessionLocal
from app.db.models import MovimientoStock
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

    resultado = await interpretar_mensaje(message_text, user)

    if not resultado["ok"]:
        if "error" in resultado:
            await context.bot.send_message(chat_id=chat_id, text=f"❌ Error: {resultado['error']}")
        else:
            campos = ", ".join(resultado["faltantes"])
            await context.bot.send_message(chat_id=chat_id, text=f"⚠️ Faltan datos: {campos}. ¿Podés completar?")
        return

    datos = resultado["datos"]
    datos["mensaje_original"] = message_text

    try:
        db = SessionLocal()
        nuevo_mov = MovimientoStock(**datos)
        db.add(nuevo_mov)
        db.commit()
        db.refresh(nuevo_mov)

        await context.bot.send_message(
            chat_id=chat_id,
            text=(
                f"✅ Movimiento registrado:\n"
                f"- Producto: {datos['producto']}\n"
                f"- Formato: {datos['formato']}\n"
                f"- Volumen: {datos['volumen_litros']} L\n"
                f"- Cliente: {datos['cliente']}\n"
                f"- Lote: {datos['lote']}\n"
                f"- Responsable: {datos['responsable']}"
            )
        )

    except Exception as e:
        await context.bot.send_message(chat_id=chat_id, text=f"💥 Error al guardar en base: {e}")
    finally:
        db.close()

async def start_bot():
    if not settings:
        print("🚫 Bot no iniciado: configuración inválida.")
        return

    try:
        application = ApplicationBuilder().token(settings.telegram_bot_token).build()
        application.add_handler(MessageHandler(filters.TEXT & (~filters.COMMAND), handle_message))
        print("🤖 Bot iniciado y escuchando mensajes...")

        # Inicializar y correr en background sin bloquear
        await application.initialize()
        await application.start()
        await application.updater.start_polling()

    except Exception as e:
        print(f"❌ Error al iniciar el bot: {e}")