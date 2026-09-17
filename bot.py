import os
import tempfile
import sqlite3

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


# ============================================================
# НАСТРОЙКИ
# ============================================================

FULL_ANALYSIS_PRICE = 100

PHOTO_DIR = "data/photos"


# ============================================================
# СОХРАНЕНИЕ ПОСЛЕДНЕЙ ФОТОГРАФИИ
# ============================================================

def save_user_photo(user_id, source_path):

    os.makedirs(PHOTO_DIR, exist_ok=True)

    destination = os.path.join(
        PHOTO_DIR,
        f"{user_id}.jpg"
    )

    with open(source_path, "rb") as source:

        with open(destination, "wb") as destination_file:

            destination_file.write(
                source.read()
            )

    return destination


def get_user_photo(user_id):

    path = os.path.join(
        PHOTO_DIR,
        f"{user_id}.jpg"
    )

    if os.path.exists(path):

        return path

    return None


# ============================================================
# START
# ============================================================

async def start(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

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

        "Я выполняю визуальный эстетический анализ "
        "фотографии лица.\n\n"

        "Анализируются видимые характеристики:\n"
        "📐 симметрия и пропорции\n"
        "🗿 нижняя треть лица\n"
        "👃 нос\n"
        "👁 орбитальная область\n"
        "💇 линия роста волос\n"
        "🧔 борода\n"
        "✨ кожа\n"
        "📸 ракурс и освещение\n\n"

        f"Бесплатно доступно "
        f"{FREE_DAILY_ANALYSES} анализа в сутки.\n\n"

        "Отправьте фотографию для начала.",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


# ============================================================
# КНОПКА "АНАЛИЗИРОВАТЬ"
# ============================================================

async def ask_for_photo(
    query
):

    await query.message.reply_text(

        "📸 Отправьте фотографию лица.\n\n"

        "Для более корректного визуального анализа "
        "желательно использовать фотографию, где:\n"
        "• лицо хорошо освещено\n"
        "• лицо не закрыто предметами\n"
        "• камера находится примерно на уровне глаз\n"
        "• изображение достаточно чёткое"
    )


# ============================================================
# ЛИМИТ
# ============================================================

async def show_limit(
    query
):

    user_id = query.from_user.id

    used = get_free_analyses(
        user_id
    )

    remaining = max(
        0,
        FREE_DAILY_ANALYSES - used
    )

    await query.message.reply_text(

        "📊 ВАШ ЛИМИТ\n\n"

        f"Бесплатных анализов сегодня: "
        f"{used}/{FREE_DAILY_ANALYSES}\n\n"

        f"Осталось: {remaining}"
    )


# ============================================================
# ИНФОРМАЦИЯ О ПОЛНОМ АНАЛИЗЕ
# ============================================================

async def show_full_analysis_info(
    query
):

    keyboard = [

        [
            InlineKeyboardButton(
                "💎 Купить полный анализ — 100 ⭐",
                callback_data="buy_full"
            )
        ]

    ]

    await query.message.reply_text(

        "💎 ПОЛНЫЙ ЭСТЕТИЧЕСКИЙ АНАЛИЗ\n\n"

        "В расширенный анализ входят:\n\n"

        "📐 подробные пропорции лица\n"
        "🗿 Mandibula — нижняя челюсть\n"
        "👤 Mentum — подбородок\n"
        "👃 Nasus — нос\n"
        "👁 Regio orbitalis — орбитальная область\n"
        "💇 Capilli — волосы\n"
        "🧔 Barba — борода\n"
        "✨ Cutis — кожа\n"
        "📸 ракурс и освещение\n"
        "👕 общая визуальная презентация\n"
        "💡 индивидуальные рекомендации\n"
        "📋 приоритетный план улучшения\n\n"

        "Стоимость: 100 ⭐\n\n"

        "После оплаты полный анализ будет "
        "выполнен для последней отправленной "
        "фотографии.",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


# ============================================================
# ОБРАБОТКА КНОПОК
# ============================================================

async def button_handler(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.callback_query

    await query.answer()

    if query.data == "analyze":

        await ask_for_photo(
            query
        )

    elif query.data == "limit":

        await show_limit(
            query
        )

    elif query.data == "full":

        await show_full_analysis_info(
            query
        )

    elif query.data == "buy_full":

        await send_full_invoice(
            query,
            context
        )


# ============================================================
# СОЗДАНИЕ СЧЁТА TELEGRAM STARS
# ============================================================

async def send_full_invoice(
    query,
    context
):

    user_id = query.from_user.id

    photo_path = get_user_photo(
        user_id
    )

    if not photo_path:

        await query.message.reply_text(

            "📸 Сначала отправьте фотографию.\n\n"
            "После этого можно приобрести полный анализ."
        )

        return

    await context.bot.send_invoice(

        chat_id=user_id,

        title="Полный эстетический анализ",

        description=(
            "Подробный визуальный анализ "
            "пропорций лица, волос, бороды, "
            "кожи, стиля и визуальной презентации."
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


# ============================================================
# PRE-CHECKOUT
# ============================================================

async def precheckout_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.pre_checkout_query

    await query.answer(
        ok=True
    )


# ============================================================
# УСПЕШНАЯ ОПЛАТА
# ============================================================

async def successful_payment(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    photo_path = get_user_photo(
        user_id
    )

    if not photo_path:

        await update.message.reply_text(

            "✅ Оплата получена.\n\n"
            "Но фотография не найдена. "
            "Пожалуйста, отправьте её ещё раз."
        )

        return

    await update.message.reply_text(

        "✅ Оплата получена.\n\n"
        "🔎 Выполняю полный анализ...\n"
        "Это может занять некоторое время."
    )

    try:

        result = analyze_image(
            photo_path,
            full=True
        )

        await send_long_message(
            update.message,
            result
        )

    except Exception as error:

        print(
            "FULL ANALYSIS ERROR:"
        )

        print(error)

        await update.message.reply_text(

            "❌ Не удалось выполнить полный анализ.\n\n"
            "Попробуйте ещё раз позже."
        )


# ============================================================
# ОТПРАВКА ДЛИННОГО СООБЩЕНИЯ
# ============================================================

async def send_long_message(
    message,
    text
):

    max_length = 4000

    for start in range(
        0,
        len(text),
        max_length
    ):

        part = text[
            start:start + max_length
        ]

        await message.reply_text(
            part
        )


# ============================================================
# ОБРАБОТКА ФОТОГРАФИИ
# ============================================================

async def handle_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    used = get_free_analyses(
        user_id
    )

    # Проверяем бесплатный лимит

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

            "Вы использовали "
            f"{FREE_DAILY_ANALYSES} бесплатных анализов.\n\n"

            "Для подробного анализа можно "
            "приобрести полный разбор.",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return

    await update.message.reply_text(
        "🔎 Анализирую фотографию..."
    )

    photo = update.message.photo[-1]

    telegram_file = await photo.get_file()

    with tempfile.NamedTemporaryFile(
        suffix=".jpg",
        delete=False
    ) as temp:

        temporary_path = temp.name

    try:

        await telegram_file.download_to_drive(
            temporary_path
        )

        # Сохраняем фотографию пользователя

        save_user_photo(
            user_id,
            temporary_path
        )

        # Краткий анализ

        result = analyze_image(
            temporary_path,
            full=False
        )

        # Засчитываем бесплатный анализ

        add_free_analysis(
            user_id
        )

        await send_long_message(
            update.message,
            result
        )

        # Показываем кнопку полного анализа

        keyboard = [

            [
                InlineKeyboardButton(
                    "💎 Полный анализ — 100 ⭐",
                    callback_data="full"
                )
            ]

        ]

        await update.message.reply_text(

            "Хотите получить подробный разбор "
            "этой фотографии?",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

    except Exception as error:

        print(
            "PHOTO ANALYSIS ERROR:"
        )

        print(error)

        await update.message.reply_text(

            "❌ Не удалось выполнить анализ.\n\n"
            "Попробуйте отправить другую фотографию."
        )

    finally:

        if os.path.exists(
            temporary_path
        ):

            os.remove(
                temporary_path
            )


# ============================================================
# ЗАПУСК
# ============================================================

def main():

    init_database()

    application = (
        Application
        .builder()
        .token(
            TELEGRAM_BOT_TOKEN
        )
        .build()
    )

    # /start

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    # Кнопки

    application.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    # Фотографии

    application.add_handler(
        MessageHandler(
            filters.PHOTO,
            handle_photo
        )
    )

    # Проверка оплаты

    application.add_handler(
        PreCheckoutQueryHandler(
            precheckout_callback
        )
    )

    # Успешная оплата

    application.add_handler(
        MessageHandler(
            filters.SUCCESSFUL_PAYMENT,
            successful_payment
        )
    )

    print(
        "================================"
    )

    print(
        "Бот запущен."
    )

    print(
        "================================"
    )

    application.run_polling()


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":

    main()
