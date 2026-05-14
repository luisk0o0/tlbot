import os
import deepl

from langdetect import detect
from deep_translator import GoogleTranslator

from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    MessageHandler,
    ContextTypes,
    filters,
)

TOKEN = os.getenv("BOT_TOKEN")
DEEPL_KEY = os.getenv("DEEPL_API_KEY")

deepl_translator = deepl.Translator(DEEPL_KEY)

TARGET_LANGUAGES = {
    "ES": "🇪🇸",
    "EN-US": "🇬🇧",
    "RU": "🇷🇺",
    "KO": "🇰🇷",
    "ZH": "🇨🇳",
}

LANG_DETECT_MAP = {
    "es": "ES",
    "en": "EN-US",
    "ru": "RU",
    "ko": "KO",
    "zh-cn": "ZH",
    "zh-tw": "ZH",
}

DEEPL_LANGS = ["ES", "EN-US", "RU"]

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

        # Google
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

    if not update.message or not update.message.text:
        return

    text = update.message.text.strip()

    # Ignorar mensajes cortos
    if len(text) < 2:
        return

    # Ignorar comandos
    if text.startswith("/"):
        return

    try:

        detected_lang = detect(text)

        source_lang = LANG_DETECT_MAP.get(detected_lang)

        translations = []

        for lang_code, flag in TARGET_LANGUAGES.items():

            # No traducir al idioma original
            if lang_code == source_lang:
                continue

            translated = translate_text(text, lang_code)

            if translated:

                translations.append(
                    f"{flag} {translated}"
                )

        if translations:

            final_text = "\n\n".join(translations)

            await update.message.reply_text(
                final_text,
                reply_to_message_id=update.message.message_id
            )

    except Exception as e:
        print("Error:", e)

app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(
    MessageHandler(
        filters.TEXT & ~filters.COMMAND,
        translate_message
    )
)

print("Bot iniciado...")

app.run_polling()