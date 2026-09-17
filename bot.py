import os
import tempfile
from telegram import (
    Update,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    LabeledPrice,
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    PreCheckoutQueryHandler,
    ContextTypes,
    filters,
)
from config import (
    TELEGRAM_BOT_TOKEN,
    FREE_DAILY_ANALYSES,
)
from database import (
    init_database,
    get_free_analyses,
    add_free_analysis,
)
from analyzer import analyze_image
from image_generator import generate_improved_photo

FULL_ANALYSIS_PRICE = 100
PHOTO_DIR = "data/photos"


def save_user_photo(user_id, source_path):
    os.makedirs(PHOTO_DIR, exist_ok=True)
    destination = os.path.join(PHOTO_DIR, f"{user_id}.jpg")
    with open(source_path, "rb") as source:
        with open(destination, "wb") as destination_file:
            destination_file.write(source.read())
    return destination


def get_user_photo(user_id):
    path = os.path.join(PHOTO_DIR, f"{user_id}.jpg")
    if os.path.exists(path):
        return path
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📸 Анализировать фотографию", callback_data="analyze")],
        [InlineKeyboardButton("📊 Мой лимит", callback_data="limit")],
        [InlineKeyboardButton("💎 Полный анализ — 100 ⭐", callback_data="full")],
    ]
    await update.message.reply_text(
        "Здравствуйте! 👋\n\n"
        "Я делаю looksmaxxing-анализ лица по фотографии.\n\n"
        "В бесплатном анализе вы получите:\n"
        "⭐ PSL-оценку + тир\n"
        "⭐ APPIL-оценку\n"
        "📐 Разбор пропорций и костной структуры\n"
        "👁️ Глаза, нос, челюсть, подбородок\n"
        "💇 Волосы и растительность\n"
        "🎨 + Улучшенную версию фотографии\n\n"
        f"Бесплатно: {FREE_DAILY_ANALYSES} анализа в сутки.\n\n"
        "Просто отправьте фотографию.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def ask_for_photo(query):
    await query.message.reply_text(
        "📸 Отправьте фотографию лица.\n\n"
        "Рекомендации для лучшего результата:\n"
        "• хорошее освещение\n"
        "• лицо полностью в кадре\n"
        "• камера на уровне глаз\n"
        "• без сильных фильтров"
    )


async def show_limit(query):
    user_id = query.from_user.id
    used = get_free_analyses(user_id)
    remaining = max(0, FREE_DAILY_ANALYSES - used)

    await query.message.reply_text(
        "📊 Ваш лимит\n\n"
        f"Использовано сегодня: {used}/{FREE_DAILY_ANALYSES}\n"
        f"Осталось: {remaining}"
    )


async def show_full_analysis_info(query):
    keyboard = [
        [InlineKeyboardButton("💎 Купить полный анализ — 100 ⭐", callback_data="buy_full")]
    ]
    await query.message.reply_text(
        "💎 Полный looksmaxxing-анализ\n\n"
        "Вы получите:\n"
        "⭐ Точную PSL + APPIL оценку\n"
        "📐 Подробный разбор всех зон лица\n"
        "👁️ Hunter eyes, canthal tilt, jawline и т.д.\n"
        "💡 Конкретные soft-maxxing рекомендации\n"
        "🎯 Приоритетные наблюдения\n\n"
        "Стоимость: 100 ⭐",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "analyze":
        await ask_for_photo(query)
    elif query.data == "limit":
        await show_limit(query)
    elif query.data == "full":
        await show_full_analysis_info(query)
    elif query.data == "buy_full":
        await send_full_invoice(query, context)


async def send_full_invoice(query, context):
    user_id = query.from_user.id
    photo_path = get_user_photo(user_id)

    if not photo_path:
        await query.message.reply_text(
            "📸 Сначала отправьте фотографию.\n"
            "После этого можно купить полный анализ."
        )
        return

    await context.bot.send_invoice(
        chat_id=user_id,
        title="Полный looksmaxxing-анализ",
        description="Полный PSL + APPIL разбор с рекомендациями",
        payload=f"full_analysis:{user_id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice("Полный анализ", FULL_ANALYSIS_PRICE)]
    )


async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo_path = get_user_photo(user_id)

    if not photo_path:
        await update.message.reply_text(
            "✅ Оплата получена, но фотография не найдена.\n"
            "Отправьте фото ещё раз."
        )
        return

    await update.message.reply_text(
        "✅ Оплата получена!\n\n"
        "🔎 Делаю полный анализ...\n"
        "⭐ Считаю PSL и APPIL\n"
        "⏳ Подождите."
    )

    try:
        result = analyze_image(photo_path, full=True)
        await send_long_message(update.message, result)
    except Exception as error:
        print("FULL ANALYSIS ERROR:", error)
        await update.message.reply_text(
            "❌ Не удалось выполнить полный анализ.\n"
            f"Ошибка: {error}"
        )


async def send_long_message(message, text):
    max_length = 4000
    for start in range(0, len(text), max_length):
        await message.reply_text(text[start:start + max_length])


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    used = get_free_analyses(user_id)

    if used >= FREE_DAILY_ANALYSES:
        keyboard = [[InlineKeyboardButton("💎 Полный анализ — 100 ⭐", callback_data="full")]]
        await update.message.reply_text(
            "🔒 Бесплатный лимит на сегодня исчерпан.\n\n"
            f"Вы использовали {FREE_DAILY_ANALYSES} анализов.\n"
            "Можно купить полный разбор.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await update.message.reply_text(
        "🔎 Анализирую фотографию...\n"
        "⭐ Считаю PSL и APPIL\n"
        "⏳ Подождите."
    )

    photo = update.message.photo[-1]
    telegram_file = await photo.get_file()

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
        temporary_path = temp.name

    try:
        await telegram_file.download_to_drive(temporary_path)
        save_user_photo(user_id, temporary_path)

        # Анализ
        result = analyze_image(temporary_path, full=False)
        add_free_analysis(user_id)
        await send_long_message(update.message, result)

        # Генерация улучшенного фото
        await update.message.reply_text("🎨 Создаю улучшенную версию фотографии...")

        try:
            improved_photo = generate_improved_photo(temporary_path)
            with open(improved_photo, "rb") as photo_file:
                await update.message.reply_photo(
                    photo=photo_file,
                    caption="✨ Готово! Обработанная looksmaxxing-версия."
                )
        except Exception as img_error:
            print("IMAGE GENERATION ERROR:", img_error)
            await update.message.reply_text(
                "❌ Не удалось создать улучшенную фотографию.\n\n"
                f"Ошибка: {img_error}"
            )

        # Предложение полного анализа
        keyboard = [[InlineKeyboardButton("💎 Полный анализ — 100 ⭐", callback_data="full")]]
        await update.message.reply_text(
            "💡 Хотите полный разбор с рекомендациями?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as error:
        print("PHOTO ANALYSIS ERROR:", error)
        await update.message.reply_text(
            "❌ Не удалось выполнить анализ.\n\n"
            f"Ошибка: {error}"
        )
    finally:
        if os.path.exists(temporary_path):
            os.remove(temporary_path)


def main():
    init_database()

    application = (
        Application.builder()
        .token(TELEGRAM_BOT_TOKEN)
        .build()
    )

    application.add_handler(CommandHandler("start", start))
    application.add_handler(CallbackQueryHandler(button_handler))
    application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    application.add_handler(PreCheckoutQueryHandler(precheckout_callback))
    application.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))

    print("================================")
    print("Бот запущен")
    print("================================")
    application.run_polling()


if __name__ == "__main__":
    main()
