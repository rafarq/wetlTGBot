import os
import shutil
import subprocess
from telegram import Update
from telegram.ext import Application, MessageHandler, CallbackContext
from telegram.ext.filters import TEXT

# Configuración del directorio temporal
TEMP_FOLDER = "tmp"
TRANSFERWEE_FOLDER = "transferwee"
TRANSFERWEE_SCRIPT = os.path.join(TRANSFERWEE_FOLDER, 'transferwee.py')

# Función para manejar mensajes con enlaces
async def handle_message(update: Update, context: CallbackContext):
    text = update.message.text

    # Verifica si el texto contiene un enlace de WeTransfer
    if "we.tl" in text:
        await update.message.reply_text("Enlace de WeTransfer detectado. Descargando el archivo...")

        # Verifica si la carpeta temporal y transferwee existen
        if not os.path.exists(TEMP_FOLDER):
            await update.message.reply_text(f"La carpeta {TEMP_FOLDER} no existe. Por favor, verifica la configuración.")
            return
        if not os.path.exists(os.path.join(TEMP_FOLDER, TRANSFERWEE_SCRIPT)):
            await update.message.reply_text(f"El script {TRANSFERWEE_SCRIPT} no existe en {TEMP_FOLDER}.")
            return

        # Ejecuta transferwee dentro de la carpeta temporal
        result = subprocess.run(
            ['python3', TRANSFERWEE_SCRIPT, 'download', text],
            capture_output=True,
            text=True,
            cwd=TEMP_FOLDER
        )

        # Depuración: Imprime salida estándar y error
        print("STDOUT:", result.stdout)
        print("STDERR:", result.stderr)

        if result.returncode == 0:
            # Lista los archivos descargados en la carpeta temporal excluyendo .DS_Store
            downloaded_files = [
                os.path.join(TEMP_FOLDER, f) for f in os.listdir(TEMP_FOLDER)
                if os.path.isfile(os.path.join(TEMP_FOLDER, f)) and not f.startswith("transferwee") and not f == ".DS_Store"
            ]

            if downloaded_files:
                try:
                    # Envía cada archivo descargado al usuario
                    for file_path in downloaded_files:
                        with open(file_path, 'rb') as file:
                            await update.message.reply_document(file)

                    # Elimina los archivos descargados, pero no la carpeta tmp
                    for file_path in downloaded_files:
                        os.remove(file_path)
                        print(f"Archivo {file_path} eliminado correctamente.")

                    await update.message.reply_text("Archivo(s) enviado(s) correctamente y archivos temporales eliminados.")
                except Exception as e:
                    print(f"Error al enviar o eliminar archivos en {TEMP_FOLDER}: {e}")
                    await update.message.reply_text("Hubo un problema al manejar los archivos descargados.")
            else:
                await update.message.reply_text("No se encontraron archivos en la carpeta temporal.")
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
