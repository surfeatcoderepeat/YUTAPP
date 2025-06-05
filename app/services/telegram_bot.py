# app/services/telegram_bot.py
import telegram
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters
from app.core.config import get_settings
from app.services.message_router import procesar_mensaje_general
from app.utils.db import guardar_en_base_de_datos

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

    print("[telegram_bot] 📥 Mensaje recibido:", message_text)
    await context.bot.send_message(chat_id=chat_id, text=f"📩 Recibido, {user}. Procesando tu mensaje...")

    resultado = await procesar_mensaje_general(message_text, user)
    print("[telegram_bot] 🔍 Resultado procesado:", resultado)

    if not resultado.get("ok", False):
        if "error" in resultado:
            await context.bot.send_message(chat_id=chat_id, text=f"❌ Error: {resultado['error']}")
        else:
            await context.bot.send_message(
                chat_id=chat_id,
                text="🤔 No pude clasificar tu mensaje. Podés intentar redactarlo de otra forma."
            )
        print("[telegram_bot] ⚠️ Error o mensaje no clasificable:", resultado)
        return

    datos = resultado["datos"]
    tabla_destino = resultado.get("tabla_destino")
    print("[telegram_bot] 💾 Guardando en base de datos:", datos, "→ Tabla:", tabla_destino)
    guardado = await guardar_en_base_de_datos(tabla_destino, datos, chat_id, context)
    if not guardado:
        print("[telegram_bot] ❌ Falló guardado en base de datos.")
        return

    mensaje_usuario = resultado.get("mensaje_usuario")
    if mensaje_usuario:
        print("[telegram_bot] 📤 Enviando confirmación al usuario.")
        await context.bot.send_message(chat_id=chat_id, text=mensaje_usuario)
        return

    # fallback genérico si no viene mensaje personalizado
    if isinstance(datos, list):
        texto_confirmacion = "\n\n".join(
            ["\n".join([f"- {k.replace('_', ' ').capitalize()}: {v}" for k, v in d.items() if k != "mensaje_original"]) for d in datos]
        )
    else:
        texto_confirmacion = "\n".join(
            [f"- {k.replace('_', ' ').capitalize()}: {v}" for k, v in datos.items() if k != "mensaje_original"]
        )
    print("[telegram_bot] 📤 Enviando confirmación al usuario.")
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
                handle_message
            )
        )
        print("[telegram_bot] 🤖 Bot iniciado y configurando handlers...")

        # Bloque alternativo compatible con Railway
        await application.initialize()
        await application.start()
        print("[telegram_bot] ✅ Bot activo y escuchando (start_polling)")
        await application.updater.start_polling()

    except Exception as e:
        print("[telegram_bot] ❌ Error al iniciar el bot:", e)