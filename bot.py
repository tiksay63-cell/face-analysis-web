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
        [
            InlineKeyboardButton(
                "📸 Анализировать фотографию",
                callback_data="analyze"
            )
        ],
        [
            InlineKeyboardButton(
                "📊 Мой лимит",
                callback_data="limit"
            )
        ],
        [
            InlineKeyboardButton(
                "💎 Полный анализ — 100 ⭐",
                callback_data="full"
            )
        ]
    ]
    await update.message.reply_text(
        "Здравствуйте! 👋\n\n"
        "Я выполняю looksmaxxing-анализ лица по фотографии.\n\n"
        "Что вы получите в бесплатном анализе:\n"
        "⭐ PSL-оценку (шкала + тир)\n"
        "⭐ APPIL-оценку\n"
        "📐 Facial thirds, midface ratio, maxilla\n"
        "🗿 Mandible, gonial angle, ramus, chin projection\n"
        "👁️ Hunter eyes, canthal tilt, eye set\n"
        "👃 Нос, philtrum, губы\n"
        "💇 Hairline и причёска\n"
        "🧔 Растительность на лице\n"
        "📸 Ракурс, освещение и ограничения фото\n\n"
        f"Бесплатно доступно {FREE_DAILY_ANALYSES} коротких анализа в сутки.\n\n"
        "Отправьте фотографию для начала.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def ask_for_photo(query):
    await query.message.reply_text(
        "📸 Отправьте фотографию лица.\n\n"
        "Для максимально точного анализа желательно:\n"
        "• хорошее и ровное освещение\n"
        "• лицо полностью в кадре\n"
        "• камера примерно на уровне глаз\n"
        "• нейтральное выражение лица\n"
        "• чёткое изображение без сильных фильтров"
    )


async def show_limit(query):
    user_id = query.from_user.id
    used = get_free_analyses(user_id)
    remaining = max(0, FREE_DAILY_ANALYSES - used)

    await query.message.reply_text(
        "📊 ВАШ ЛИМИТ\n\n"
        f"Использовано сегодня: {used}/{FREE_DAILY_ANALYSES}\n\n"
        f"Осталось бесплатных анализов: {remaining}"
    )


async def show_full_analysis_info(query):
    keyboard = [
        [
            InlineKeyboardButton(
                "💎 Купить полный анализ — 100 ⭐",
                callback_data="buy_full"
            )
        ]
    ]
    await query.message.reply_text(
        "💎 ПОЛНЫЙ LOOKSMAXXING-АНАЛИЗ\n\n"
        "После оплаты вы получите:\n\n"
        "⭐ Точную PSL-оценку + тир (Sub5 → Gigachad)\n"
        "⭐ APPIL-оценку\n"
        "📐 Подробный разбор facial thirds, midface ratio, maxilla\n"
        "🗿 Mandible, ramus, gonial angle, chin projection\n"
        "👁️ Hunter eyes, canthal tilt, eye set, brow ridge\n"
        "👃 Полный разбор носа (alar width, projection)\n"
        "👄 Philtrum и область губ\n"
        "💇 Hairline + причёска\n"
        "🧔 Растительность на лице\n"
        "📸 Глубокий разбор ракурса, освещения и ограничений фото\n"
        "✨ Визуальная подача\n"
        "💡 Конкретные soft-maxxing рекомендации\n"
        "🎯 Ключевые наблюдения\n\n"
        "🎨 + Обработанная версия фотографии\n"
        "(улучшенный свет, кожа, волосы, фон и общая подача)\n\n"
        "Стоимость: 100 ⭐\n\n"
        "Для покупки нажмите кнопку ниже.",
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
            "📸 Сначала отправьте фотографию.\n\n"
            "После этого можно приобрести полный анализ."
        )
        return

    await context.bot.send_invoice(
        chat_id=user_id,
        title="Полный looksmaxxing-анализ + обработка фото",
        description=(
            "Полный PSL + APPIL разбор лица "
            "и создание улучшенной версии фотографии."
        ),
        payload=f"full_analysis:{user_id}",
        provider_token="",
        currency="XTR",
        prices=[
            LabeledPrice(
                "Полный анализ",
                FULL_ANALYSIS_PRICE
            )
        ]
    )


async def precheckout_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.pre_checkout_query
    await query.answer(ok=True)


async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo_path = get_user_photo(user_id)

    if not photo_path:
        await update.message.reply_text(
            "✅ Оплата получена.\n\n"
            "Но фотография не найдена.\n"
            "Пожалуйста, отправьте её ещё раз."
        )
        return

    await update.message.reply_text(
        "✅ Оплата получена!\n\n"
        "🔎 Выполняю полный looksmaxxing-анализ...\n\n"
        "⭐ Считаю PSL и APPIL\n"
        "📐 Разбираю facial thirds и midface\n"
        "🗿 Анализирую mandible, gonial angle, chin\n"
        "👁️ Оцениваю hunter eyes и canthal tilt\n"
        "👃 Разбираю нос и philtrum\n"
        "💇 Анализирую hairline и причёску\n"
        "📸 Проверяю ракурс и освещение\n"
        "💡 Формирую рекомендации..."
    )

    try:
        result = analyze_image(photo_path, full=True)
        await send_long_message(update.message, result)

        await update.message.reply_text(
            "🎨 Анализ завершён.\n\n"
            "Теперь создаю улучшенную версию фотографии..."
        )

        improved_photo = generate_improved_photo(photo_path)

        with open(improved_photo, "rb") as photo_file:
            await update.message.reply_photo(
                photo=photo_file,
                caption=(
                    "✨ Готово!\n\n"
                    "Обработанная looksmaxxing-версия вашей фотографии."
                )
            )

    except Exception as error:
        print("FULL ANALYSIS / IMAGE ERROR:")
        print(error)
        await update.message.reply_text(
            "❌ Не удалось завершить обработку.\n\n"
            "Попробуйте ещё раз позже."
        )


async def send_long_message(message, text):
    max_length = 4000
    for start in range(0, len(text), max_length):
        part = text[start:start + max_length]
        await message.reply_text(part)


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    used = get_free_analyses(user_id)

    if used >= FREE_DAILY_ANALYSES:
        keyboard = [
            [
                InlineKeyboardButton(
                    "💎 Полный анализ — 100 ⭐",
                    callback_data="full"
                )
            ]
        ]
        await update.message.reply_text(
            "🔒 Бесплатный лимит на сегодня исчерпан.\n\n"
            f"Вы использовали {FREE_DAILY_ANALYSES} бесплатных анализов.\n\n"
            "Для получения полного PSL + APPIL разбора "
            "и обработанной фотографии можно приобрести полный анализ.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await update.message.reply_text(
        "🔎 Анализирую фотографию...\n\n"
        "⭐ Считаю PSL и APPIL\n"
        "📐 Смотрю пропорции и костную структуру\n"
        "⏳ Пожалуйста, подождите."
    )

    photo = update.message.photo[-1]
    telegram_file = await photo.get_file()

    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as temp:
        temporary_path = temp.name

    try:
        await telegram_file.download_to_drive(temporary_path)
        save_user_photo(user_id, temporary_path)

        result = analyze_image(temporary_path, full=False)
        add_free_analysis(user_id)

        await send_long_message(update.message, result)

        keyboard = [
            [
                InlineKeyboardButton(
                    "💎 Полный анализ — 100 ⭐",
                    callback_data="full"
                )
            ]
        ]
        await update.message.reply_text(
            "💡 Хотите получить полный PSL + APPIL разбор "
            "и обработанную версию этой фотографии?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as error:
        print("PHOTO ANALYSIS ERROR:")
        print(error)
        await update.message.reply_text(
            "❌ Не удалось выполнить анализ.\n\n"
            "Попробуйте отправить другую фотографию."
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
    application.add_handler(
        MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment)
    )

    print("================================")
    print("Бот запущен.")
    print("================================")
    application.run_polling()


if __name__ == "__main__":
    main()
