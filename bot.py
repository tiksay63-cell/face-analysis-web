import os
import tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    PreCheckoutQueryHandler, ContextTypes, filters
)
from config import TELEGRAM_BOT_TOKEN, FREE_DAILY_ANALYSES
from database import init_database, get_free_analyses, add_free_analysis
from analyzer import analyze_image

FULL_ANALYSIS_PRICE = 100
PHOTO_DIR = "data/photos"
CHANNEL_ID = "@myasnoibulion"
CHANNEL_LINK = "https://t.me/myasnoibulion"


def save_user_photo(user_id, source_path):
    os.makedirs(PHOTO_DIR, exist_ok=True)
    dest = os.path.join(PHOTO_DIR, f"{user_id}.jpg")
    with open(source_path, "rb") as s, open(dest, "wb") as d:
        d.write(s.read())
    return dest


def get_user_photo(user_id):
    path = os.path.join(PHOTO_DIR, f"{user_id}.jpg")
    return path if os.path.exists(path) else None


async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ("member", "administrator", "creator", "restricted")
    except Exception as e:
        print("Sub check error:", e)
        return False


async def ask_to_subscribe(update):
    keyboard = [
        [InlineKeyboardButton("Подписаться на канал", url=CHANNEL_LINK)],
        [InlineKeyboardButton("Я подписался", callback_data="check_sub")]
    ]
    text = (
        "Чтобы пользоваться ботом — подпишись на канал.\n\n"
        "1. Нажми «Подписаться»\n"
        "2. Подпишись\n"
        "3. Вернись и нажми «Я подписался»"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def start(update, context):
    if not await check_subscription(update.effective_user.id, context):
        await ask_to_subscribe(update)
        return

    keyboard = [
        [InlineKeyboardButton("Анализировать фото", callback_data="analyze")],
        [InlineKeyboardButton("Мой лимит", callback_data="limit")],
        [InlineKeyboardButton("Полный анализ — 100 Stars", callback_data="full")],
    ]
    await update.message.reply_text(
        "Looksmaxxing-анализ лица.\n\n"
        "Бесплатно:\n"
        "• PSL + APPIL\n"
        "• Тир (Sub3 → Chad)\n"
        "• Прямой разбор слабостей\n\n"
        "Полный анализ (100 Stars):\n"
        "• Конкретные рекомендации\n\n"
        f"Лимит: {FREE_DAILY_ANALYSES} в сутки.\n"
        "Кидай фото.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def ask_for_photo(query):
    await query.message.reply_text(
        "Кидай фото лица.\n"
        "Лучше: ровный свет, лицо в кадре, камера на уровне глаз, без фильтров."
    )


async def show_limit(query):
    used = get_free_analyses(query.from_user.id)
    remaining = max(0, FREE_DAILY_ANALYSES - used)
    await query.message.reply_text(
        f"Лимит\nИспользовано: {used}/{FREE_DAILY_ANALYSES}\nОсталось: {remaining}"
    )


async def show_full_info(query):
    keyboard = [[InlineKeyboardButton("Купить — 100 Stars", callback_data="buy_full")]]
    await query.message.reply_text(
        "Полный разбор\n\n"
        "• Точный PSL + тир\n"
        "• Разбор всех зон\n"
        "• Конкретные soft-maxxing рекомендации\n\n"
        "100 Stars",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id

    if query.data == "check_sub":
        if await check_subscription(uid, context):
            await query.message.reply_text("Подписка ок. Можно пользоваться.")
            keyboard = [
                [InlineKeyboardButton("Анализировать фото", callback_data="analyze")],
                [InlineKeyboardButton("Мой лимит", callback_data="limit")],
                [InlineKeyboardButton("Полный анализ — 100 Stars", callback_data="full")],
            ]
            await query.message.reply_text("Выбери:", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.message.reply_text("Ещё не подписан. Подпишись и нажми снова.")
        return

    if not await check_subscription(uid, context):
        await ask_to_subscribe(update)
        return

    if query.data == "analyze":
        await ask_for_photo(query)
    elif query.data == "limit":
        await show_limit(query)
    elif query.data == "full":
        await show_full_info(query)
    elif query.data == "buy_full":
        await send_invoice(query, context)


async def send_invoice(query, context):
    path = get_user_photo(query.from_user.id)
    if not path:
        await query.message.reply_text("Сначала кинь фото.")
        return
    await context.bot.send_invoice(
        chat_id=query.from_user.id,
        title="Полный looksmaxxing-анализ",
        description="PSL + APPIL + конкретные рекомендации",
        payload=f"full:{query.from_user.id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice("Полный анализ", FULL_ANALYSIS_PRICE)]
    )


async def precheckout(update, context):
    await update.pre_checkout_query.answer(ok=True)


async def successful_payment(update, context):
    uid = update.effective_user.id
    path = get_user_photo(uid)
    if not path:
        await update.message.reply_text("Оплата прошла, но фото нет. Кинь ещё раз.")
        return
    await update.message.reply_text("Оплата получена. Делаю полный разбор...")
    try:
        result = analyze_image(path, full=True)
        await send_long(update.message, result)
    except Exception as e:
        print(e)
        await update.message.reply_text(f"Ошибка: {e}")


async def send_long(message, text):
    for i in range(0, len(text), 4000):
        await message.reply_text(text[i:i+4000])


async def handle_photo(update, context):
    uid = update.effective_user.id
    if not await check_subscription(uid, context):
        await ask_to_subscribe(update)
        return

    used = get_free_analyses(uid)
    if used >= FREE_DAILY_ANALYSES:
        keyboard = [[InlineKeyboardButton("Полный анализ — 100 Stars", callback_data="full")]]
        await update.message.reply_text(
            f"Лимит на сегодня кончился ({FREE_DAILY_ANALYSES}).\nМожно купить полный разбор.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await update.message.reply_text("Считаю PSL и APPIL...")

    photo = update.message.photo[-1]
    tg_file = await photo.get_file()
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        path = tmp.name

    try:
        await tg_file.download_to_drive(path)
        save_user_photo(uid, path)
        result = analyze_image(path, full=False)
        add_free_analysis(uid)
        await send_long(update.message, result)

        keyboard = [[InlineKeyboardButton("Полный анализ — 100 Stars", callback_data="full")]]
        await update.message.reply_text(
            "Нужны конкретные рекомендации — бери полный разбор.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        print(e)
        await update.message.reply_text(f"Ошибка анализа: {e}")
    finally:
        if os.path.exists(path):
            os.remove(path)


def main():
    init_database()
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    print("Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()import os
import tempfile
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, LabeledPrice
from telegram.ext import (
    Application, CommandHandler, MessageHandler, CallbackQueryHandler,
    PreCheckoutQueryHandler, ContextTypes, filters
)
from config import TELEGRAM_BOT_TOKEN, FREE_DAILY_ANALYSES
from database import init_database, get_free_analyses, add_free_analysis
from analyzer import analyze_image

FULL_ANALYSIS_PRICE = 100
PHOTO_DIR = "data/photos"
CHANNEL_ID = "@myasnoibulion"
CHANNEL_LINK = "https://t.me/myasnoibulion"


def save_user_photo(user_id, source_path):
    os.makedirs(PHOTO_DIR, exist_ok=True)
    dest = os.path.join(PHOTO_DIR, f"{user_id}.jpg")
    with open(source_path, "rb") as s, open(dest, "wb") as d:
        d.write(s.read())
    return dest


def get_user_photo(user_id):
    path = os.path.join(PHOTO_DIR, f"{user_id}.jpg")
    return path if os.path.exists(path) else None


async def check_subscription(user_id, context):
    try:
        member = await context.bot.get_chat_member(chat_id=CHANNEL_ID, user_id=user_id)
        return member.status in ("member", "administrator", "creator", "restricted")
    except Exception as e:
        print("Sub check error:", e)
        return False


async def ask_to_subscribe(update):
    keyboard = [
        [InlineKeyboardButton("Подписаться на канал", url=CHANNEL_LINK)],
        [InlineKeyboardButton("Я подписался", callback_data="check_sub")]
    ]
    text = (
        "Чтобы пользоваться ботом — подпишись на канал.\n\n"
        "1. Нажми «Подписаться»\n"
        "2. Подпишись\n"
        "3. Вернись и нажми «Я подписался»"
    )
    if update.message:
        await update.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))
    elif update.callback_query:
        await update.callback_query.message.reply_text(text, reply_markup=InlineKeyboardMarkup(keyboard))


async def start(update, context):
    if not await check_subscription(update.effective_user.id, context):
        await ask_to_subscribe(update)
        return

    keyboard = [
        [InlineKeyboardButton("Анализировать фото", callback_data="analyze")],
        [InlineKeyboardButton("Мой лимит", callback_data="limit")],
        [InlineKeyboardButton("Полный анализ — 100 Stars", callback_data="full")],
    ]
    await update.message.reply_text(
        "Looksmaxxing-анализ лица.\n\n"
        "Бесплатно:\n"
        "• PSL + APPIL\n"
        "• Тир (Sub3 → Chad)\n"
        "• Прямой разбор слабостей\n\n"
        "Полный анализ (100 Stars):\n"
        "• Конкретные рекомендации\n\n"
        f"Лимит: {FREE_DAILY_ANALYSES} в сутки.\n"
        "Кидай фото.",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def ask_for_photo(query):
    await query.message.reply_text(
        "Кидай фото лица.\n"
        "Лучше: ровный свет, лицо в кадре, камера на уровне глаз, без фильтров."
    )


async def show_limit(query):
    used = get_free_analyses(query.from_user.id)
    remaining = max(0, FREE_DAILY_ANALYSES - used)
    await query.message.reply_text(
        f"Лимит\nИспользовано: {used}/{FREE_DAILY_ANALYSES}\nОсталось: {remaining}"
    )


async def show_full_info(query):
    keyboard = [[InlineKeyboardButton("Купить — 100 Stars", callback_data="buy_full")]]
    await query.message.reply_text(
        "Полный разбор\n\n"
        "• Точный PSL + тир\n"
        "• Разбор всех зон\n"
        "• Конкретные soft-maxxing рекомендации\n\n"
        "100 Stars",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )


async def button_handler(update, context):
    query = update.callback_query
    await query.answer()
    uid = query.from_user.id

    if query.data == "check_sub":
        if await check_subscription(uid, context):
            await query.message.reply_text("Подписка ок. Можно пользоваться.")
            keyboard = [
                [InlineKeyboardButton("Анализировать фото", callback_data="analyze")],
                [InlineKeyboardButton("Мой лимит", callback_data="limit")],
                [InlineKeyboardButton("Полный анализ — 100 Stars", callback_data="full")],
            ]
            await query.message.reply_text("Выбери:", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            await query.message.reply_text("Ещё не подписан. Подпишись и нажми снова.")
        return

    if not await check_subscription(uid, context):
        await ask_to_subscribe(update)
        return

    if query.data == "analyze":
        await ask_for_photo(query)
    elif query.data == "limit":
        await show_limit(query)
    elif query.data == "full":
        await show_full_info(query)
    elif query.data == "buy_full":
        await send_invoice(query, context)


async def send_invoice(query, context):
    path = get_user_photo(query.from_user.id)
    if not path:
        await query.message.reply_text("Сначала кинь фото.")
        return
    await context.bot.send_invoice(
        chat_id=query.from_user.id,
        title="Полный looksmaxxing-анализ",
        description="PSL + APPIL + конкретные рекомендации",
        payload=f"full:{query.from_user.id}",
        provider_token="",
        currency="XTR",
        prices=[LabeledPrice("Полный анализ", FULL_ANALYSIS_PRICE)]
    )


async def precheckout(update, context):
    await update.pre_checkout_query.answer(ok=True)


async def successful_payment(update, context):
    uid = update.effective_user.id
    path = get_user_photo(uid)
    if not path:
        await update.message.reply_text("Оплата прошла, но фото нет. Кинь ещё раз.")
        return
    await update.message.reply_text("Оплата получена. Делаю полный разбор...")
    try:
        result = analyze_image(path, full=True)
        await send_long(update.message, result)
    except Exception as e:
        print(e)
        await update.message.reply_text(f"Ошибка: {e}")


async def send_long(message, text):
    for i in range(0, len(text), 4000):
        await message.reply_text(text[i:i+4000])


async def handle_photo(update, context):
    uid = update.effective_user.id
    if not await check_subscription(uid, context):
        await ask_to_subscribe(update)
        return

    used = get_free_analyses(uid)
    if used >= FREE_DAILY_ANALYSES:
        keyboard = [[InlineKeyboardButton("Полный анализ — 100 Stars", callback_data="full")]]
        await update.message.reply_text(
            f"Лимит на сегодня кончился ({FREE_DAILY_ANALYSES}).\nМожно купить полный разбор.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
        return

    await update.message.reply_text("Считаю PSL и APPIL...")

    photo = update.message.photo[-1]
    tg_file = await photo.get_file()
    with tempfile.NamedTemporaryFile(suffix=".jpg", delete=False) as tmp:
        path = tmp.name

    try:
        await tg_file.download_to_drive(path)
        save_user_photo(uid, path)
        result = analyze_image(path, full=False)
        add_free_analysis(uid)
        await send_long(update.message, result)

        keyboard = [[InlineKeyboardButton("Полный анализ — 100 Stars", callback_data="full")]]
        await update.message.reply_text(
            "Нужны конкретные рекомендации — бери полный разбор.",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )
    except Exception as e:
        print(e)
        await update.message.reply_text(f"Ошибка анализа: {e}")
    finally:
        if os.path.exists(path):
            os.remove(path)


def main():
    init_database()
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo))
    app.add_handler(PreCheckoutQueryHandler(precheckout))
    app.add_handler(MessageHandler(filters.SUCCESSFUL_PAYMENT, successful_payment))
    print("Бот запущен")
    app.run_polling()


if __name__ == "__main__":
    main()
