import os
import subprocess
from telegram import Update
from telegram.ext import Application, MessageHandler, CallbackContext
from telegram.ext.filters import TEXT

# Función para manejar mensajes con enlaces
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text

    # Verifica si el texto contiene un enlace de WeTransfer
    if "we.tl" in text:
        await update.message.reply_text("Enlace de WeTransfer detectado. Descargando el archivo...")

        # Ejecuta transferwee para descargar el archivo
        result = subprocess.run(['python3', 'transferwee/transferwee.py', 'download', text],
                                capture_output=True, text=True)

        # Depuración: Imprime salida estándar y error
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        if result.returncode == 0:
            # Busca el archivo descargado en el directorio actual, excluyendo archivos no deseados
            downloaded_files = [
                f for f in os.listdir(".")
                if os.path.isfile(f) and not f.endswith('.py') and not f.startswith('.')
            ]

            if downloaded_files:
                # Envía cada archivo descargado al usuario
                for downloaded_file in downloaded_files:
                    with open(downloaded_file, 'rb') as file:
                        await update.message.reply_document(file)
                    # Elimina el archivo después de enviarlo
                    os.remove(downloaded_file)
                await update.message.reply_text("Archivo(s) enviado(s) correctamente.")
            else:
                await update.message.reply_text("No se pudo encontrar el archivo descargado.")
        else:
            await update.message.reply_text(f"Error al descargar el archivo. Verifica el enlace.\n{result.stderr}")
    else:
        await update.message.reply_text("Por favor, envíame un enlace válido de WeTransfer.")

# Configurar el bot
def main():
    TOKEN = "BOT TOKEN"  # Reemplaza con el token de tu bot

    # Crea la aplicación
    application = Application.builder().token(TOKEN).build()

    # Maneja mensajes de texto
    application.add_handler(MessageHandler(TEXT, handle_message))

    # Inicia el bot
    application.run_polling()

if __name__ == "__main__":
    main()