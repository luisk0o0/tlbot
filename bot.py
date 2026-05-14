import os
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

# Idiomas que usará DeepL
DEEPL_LANGS = ["ES", "EN", "RU"]

# Idiomas que usará Google Translate
GOOGLE_LANGS = ["KO", "ZH"]


def translate_text(text, target_lang):

    try:

        # Traducciones con DeepL
        if target_lang in DEEPL_LANGS:

            result = deepl_translator.translate_text(
                text,
                target_lang=target_lang
            )

            return result.text

        # Traducciones con Google Translate
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

    # Ignorar mensajes vacíos
    if not update.message or not update.message.text:
        return

    # Ignorar bots
    if update.effective_user.is_bot:
        return

    text = update.message.text.strip()

    # Ignorar mensajes cortos
    if len(text) < 2:
        return

    # Ignorar comandos
    if text.startswith("/"):
        return

    # Ignorar links
    if "http" in text:
        return

    try:

        # Detectar idioma con DeepL
        detected = deepl_translator.translate_text(
            text,
            target_lang="EN"
        )

        source_lang = detected.detected_source_lang

        print("Detected language:", source_lang)

        translations = []

        for lang_code, flag in TARGET_LANGUAGES.items():

            # NO traducir al idioma original
            if lang_code == source_lang:
                continue

            translated = translate_text(text, lang_code)

            print(lang_code, translated)

            if translated:

                translations.append(
                    f"{flag} {translated}"
                )

        # Enviar traducciones
        if translations:

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
        print("Error:", e)


# Crear aplicación
app = ApplicationBuilder().token(TOKEN).build()

# Escuchar mensajes
app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        translate_message
    )
)

print("Bot iniciado...")

# Ejecutar bot
app.run_polling()