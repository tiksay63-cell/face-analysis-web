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

FULL_ANALYSIS_PRICE = 100
PHOTO_DIR = "data/photos"

# ===== КАНАЛ =====
CHANNEL_ID = "@myasnoibulion"
CHANNEL_LINK = "https://t.me/myasnoibulion"


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


async def check_subscription(user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
    try:
        member = await context.bot.get_chat_member(
            chat_id=CHANNEL_ID,
            user_id=user_id
        )
        return member.status in ("member", "administrator", "creator")
    except Exception as e:
        print("Subscription check error:", e)
        return False


async def ask_to_subscribe(update: Update):
    keyboard = [
        [InlineKeyboardButton("📢 Подписаться на канал", url=CHANNEL_LINK)],
        [InlineKeyboardButton("✅ Я подписался", callback_data="check_sub")]
    ]
    text = (
        "🔒 Чтобы пользоваться ботом, нужно подписаться на канал.\n\n"
        "1. Нажми «Подписаться на канал»\n"
        "2. Подпишись\n"
        "3. Вернись и нажми «Я подписался»"
    )

    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    if not await check_subscription(user_id, context):
        await ask_to_subscribe(update)
        return

    keyboard = [
        [InlineKeyboardButton("📸 Анализировать фотографию", callback_data="analyze")],
        [InlineKeyboardButton("📊 Мой лимит", callback_data="limit")],
        [InlineKeyboardButton("💎 Полный анализ — 100 ⭐", callback_data="full")],
    ]
    await update.message.reply_text(
        "Здравствуйте! 👋\n\n"
        "Я делаю looksmaxxing-анализ лица по фотографии.\n\n"
        "Бесплатный анализ:\n"
        "⭐ PSL + APPIL оценка\n"
        "📐 Разбор пропорций и структуры\n"
        "⚠️ Намёки, что можно улучшить\n\n"
        "Полный анализ (100 ⭐):\n"
        "💡 Конкретные soft-maxxing рекомендации\n\n"
        f"Бесплатно: {FREE_DAILY_ANALYSES} анализа в сутки.\n\n"
        "Просто отправьте фотографию.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def ask_for_photo(query):
    await query.message.reply_text(
        "📸 Отправьте фотографию лица.\n\n"
        "Рекомендации:\n"
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
        "📐 Подробный разбор всех зон\n"
        "💡 Конкретные рекомендации, что и как улучшить\n"
        "🎯 Приоритетные наблюдения\n\n"
        "Стоимость: 100 ⭐",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # Проверка подписки на кнопку "Я подписался"
    if query.data == "check_sub":
        if await check_subscription(user_id, context):
            await query.message.reply_text("✅ Подписка подтверждена! Теперь можешь пользоваться ботом.")
            # Показываем стартовое меню
            keyboard = [
                [InlineKeyboardButton("📸 Анализировать фотографию", callback_data="analyze")],
                [InlineKeyboardButton("📊 Мой лимит", callback_data="limit")],
                [InlineKeyboardButton("💎 Полный анализ — 100 ⭐", callback_data="full")],
            ]
            await query.message.reply_text(
                "Выберите действие:",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
        else:
            await query.message.reply_text("❌ Ты ещё не подписан. Подпишись и нажми кнопку снова.")
        return

    # Для всех остальных кнопок тоже проверяем подписку
    if not await check_subscription(user_id, context):
        await ask_to_subscribe(update)
        return

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
        description="Полный PSL + APPIL разбор с конкретными рекомендациями",
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
        "💡 Готовлю рекомендации..."
    )

    try:
        result = analyze_image(photo_path, full=True)
        await send_long_message(update.message, result)
    except Exception as error:
        print("FULL ANALYSIS ERROR:", error)
        await update.message.reply_text(
            f"❌ Не удалось выполнить полный анализ.\nОшибка: {error}"
        )


async def send_long_message(message, text):
    max_length = 4000
    for start in range(0, len(text), max_length):
        await message.reply_text(text[start:start + max_length])


async def handle_photo(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id

    # Проверка подписки
    if not await check_subscription(user_id, context):
        await ask_to_subscribe(update)
        return

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

        result = analyze_image(temporary_path, full=False)
        add_free_analysis(user_id)
        await send_long_message(update.message, result)

        keyboard = [[InlineKeyboardButton("💎 Полный анализ — 100 ⭐", callback_data="full")]]
        await update.message.reply_text(
            "💡 Хотите узнать конкретные рекомендации, как улучшить результат?",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    except Exception as error:
        print("PHOTO ANALYSIS ERROR:", error)
        await update.message.reply_text(
            f"❌ Не удалось выполнить анализ.\nОшибка: {error}"
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
