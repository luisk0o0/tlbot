import os
import re
import deepl

from deep_translator import GoogleTranslator

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

# Variables de entorno
TOKEN = os.getenv("BOT_TOKEN")
DEEPL_API_KEY = os.getenv("DEEPL_API_KEY")

# Inicializar DeepL
deepl_translator = deepl.Translator(DEEPL_API_KEY)

# Idiomas del clan
TARGET_LANGUAGES = {
    "ES": "🇪🇸",
    "EN": "🇬🇧",
    "RU": "🇷🇺",
    "KO": "🇰🇷",
    "ZH": "🇨🇳",
}

# Idiomas para DeepL
DEEPL_LANGS = ["ES", "EN", "RU"]

# Idiomas para Google
GOOGLE_LANGS = ["KO", "ZH"]


def translate_text(text, target_lang):

    try:

        # DeepL
        if target_lang in DEEPL_LANGS:

            result = deepl_translator.translate_text(
                text,
                target_lang=target_lang
            )

            return result.text

        # Google Translate
        elif target_lang in GOOGLE_LANGS:

            google_map = {
                "KO": "ko",
                "ZH": "zh-CN",
            }

            return GoogleTranslator(
                source="auto",
                target=google_map[target_lang]
            ).translate(text)

    except Exception as e:
        print("Translation error:", e)
        return None


async def translate_message(update: Update, context: ContextTypes.DEFAULT_TYPE):

    try:

        if not update.message:
            return

        # Ignorar bots
        if update.effective_user.is_bot:
            return

        text = ""

        # Texto normal
        if update.message.text:
            text = update.message.text.strip()

        # Caption de imagen/video/documento
        elif update.message.caption:
            text = update.message.caption.strip()

        if not text:
            return

        # Ignorar mensajes muy cortos
        if len(text) < 2:
            return

        # Ignorar comandos
        if text.startswith("/"):
            return

        # Extraer URLs
        urls = re.findall(r'https?://\S+', text)

        # Reemplazar temporalmente URLs
        temp_text = text

        for i, url in enumerate(urls):

            temp_text = temp_text.replace(
                url,
                f"__URL{i}__"
            )

        translations = []

        for lang_code, flag in TARGET_LANGUAGES.items():

            translated = translate_text(
                temp_text,
                lang_code
            )

            if not translated:
                continue

            # Restaurar URLs
            for i, url in enumerate(urls):

                translated = translated.replace(
                    f"__URL{i}__",
                    url
                )

            # Ignorar traducciones iguales
            if translated.strip().lower() == text.strip().lower():
                continue

            translations.append(
                f"{flag} {translated}"
            )

        # Si no hay traducciones
        if not translations:
            return

        sender_name = update.effective_user.first_name

        final_text = (
            f"🗣 {sender_name}:\n"
            f"{text}\n\n"
            + "\n\n".join(translations)
        )

        await update.message.reply_text(
            final_text,
            reply_to_message_id=update.message.message_id
        )

    except Exception as e:
        print("Main error:", e)


# Crear aplicación
app = ApplicationBuilder().token(TOKEN).build()

# Escuchar texto y captions
app.add_handler(
    MessageHandler(
        (filters.TEXT | filters.CAPTION)
        & ~filters.COMMAND,
        translate_message
    )
)

print("Bot iniciado...")

# Ejecutar bot
app.run_polling()