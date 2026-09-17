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


def save_user_photo(user_id, source_path):

    os.makedirs(
        PHOTO_DIR,
        exist_ok=True
    )

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
                "💎 Расширенный анализ — 100 Stars",
                callback_data="full"
            )
        ]

    ]

    await update.message.reply_text(

        "Здравствуйте! 👋\n\n"

        "Я выполняю визуальный анализ "
        "фотографии лица.\n\n"

        "Анализируются видимые характеристики:\n"
        "📐 пропорции и симметрия\n"
        "🗿 нижняя треть лица\n"
        "👤 подбородок\n"
        "👁️ глаза и орбитальная зона\n"
        "👃 нос\n"
        "💇 волосы\n"
        "🧔 растительность на лице\n"
        "📸 ракурс и освещение\n"
        "✨ визуальная подача\n\n"

        f"Бесплатно доступно "
        f"{FREE_DAILY_ANALYSES} анализа в сутки.\n\n"

        "Отправьте фотографию для начала.",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


async def ask_for_photo(query):

    await query.message.reply_text(

        "📸 Отправьте фотографию лица.\n\n"

        "Для более корректного анализа желательно:\n"
        "• хорошее освещение\n"
        "• лицо полностью видно\n"
        "• камера примерно на уровне глаз\n"
        "• фотография достаточно чёткая\n"
        "• без сильных фильтров"
    )


async def show_limit(query):

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

        f"Использовано сегодня: "
        f"{used}/{FREE_DAILY_ANALYSES}\n\n"

        f"Осталось бесплатных анализов: "
        f"{remaining}"
    )


async def show_full_analysis_info(query):

    keyboard = [

        [
            InlineKeyboardButton(
                "💎 Купить за 100 Stars",
                callback_data="buy_full"
            )
        ]

    ]

    await query.message.reply_text(

        "💎 РАСШИРЕННЫЙ ВИЗУАЛЬНЫЙ АНАЛИЗ\n\n"

        "В расширенный разбор входят:\n\n"

        "📐 подробные пропорции\n"
        "🗿 нижняя треть лица\n"
        "👤 подбородок\n"
        "👁️ глаза и орбитальная зона\n"
        "👃 визуальный разбор носа\n"
        "👄 область рта\n"
        "💇 волосы и линия роста\n"
        "🧔 растительность на лице\n"
        "📸 ракурс и освещение\n"
        "✨ визуальная подача\n"
        "💡 индивидуальные рекомендации\n"
        "🎯 приоритетный план\n\n"

        "Стоимость: 100 Telegram Stars.\n\n"

        "После оплаты расширенный анализ будет "
        "выполнен для последней отправленной "
        "фотографии.",

        reply_markup=InlineKeyboardMarkup(
            keyboard
        )
    )


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

            "После этого можно приобрести "
            "расширенный анализ."
        )

        return

    await context.bot.send_invoice(

        chat_id=user_id,

        title="Расширенный визуальный анализ",

        description=(
            "Подробный визуальный анализ "
            "фотографии и рекомендации "
            "по визуальной подаче."
        ),

        payload=f"full_analysis:{user_id}",

        provider_token="",

        currency="XTR",

        prices=[
            LabeledPrice(
                "Расширенный анализ",
                FULL_ANALYSIS_PRICE
            )
        ]
    )


async def precheckout_callback(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    query = update.pre_checkout_query

    await query.answer(
        ok=True
    )


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

            "Но последняя фотография не найдена.\n"
            "Пожалуйста, отправьте фотографию ещё раз."
        )

        return

    await update.message.reply_text(

        "💎 Оплата получена!\n\n"

        "🔎 Выполняю расширенный анализ...\n\n"

        "📐 Проверяю пропорции\n"
        "🗿 Анализирую нижнюю треть\n"
        "👁️ Анализирую область глаз\n"
        "👃 Анализирую нос\n"
        "💇 Анализирую волосы\n"
        "📸 Проверяю фотографию\n"
        "💡 Подготавливаю рекомендации..."
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

        print(
            error
        )

        await update.message.reply_text(

            "❌ Не удалось выполнить "
            "расширенный анализ.\n\n"

            "Попробуйте ещё раз позже."
        )


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


async def handle_photo(
    update: Update,
    context: ContextTypes.DEFAULT_TYPE
):

    user_id = update.effective_user.id

    used = get_free_analyses(
        user_id
    )

    if used >= FREE_DAILY_ANALYSES:

        keyboard = [

            [
                InlineKeyboardButton(
                    "💎 Расширенный анализ — 100 Stars",
                    callback_data="full"
                )
            ]

        ]

        await update.message.reply_text(

            "🔒 Бесплатный лимит на сегодня исчерпан.\n\n"

            f"Использовано: "
            f"{FREE_DAILY_ANALYSES}/"
            f"{FREE_DAILY_ANALYSES}\n\n"

            "Для получения расширенного разбора "
            "можно приобрести полный анализ.",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

        return

    await update.message.reply_text(

        "🔎 Анализирую фотографию...\n\n"
        "⏳ Пожалуйста, подождите."
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

        save_user_photo(
            user_id,
            temporary_path
        )

        result = analyze_image(
            temporary_path,
            full=False
        )

        add_free_analysis(
            user_id
        )

        await send_long_message(
            update.message,
            result
        )

        keyboard = [

            [
                InlineKeyboardButton(
                    "💎 Расширенный разбор — 100 Stars",
                    callback_data="full"
                )
            ]

        ]

        await update.message.reply_text(

            "💡 Хотите получить расширенный "
            "разбор этой фотографии?",

            reply_markup=InlineKeyboardMarkup(
                keyboard
            )
        )

    except Exception as error:

        print(
            "PHOTO ANALYSIS ERROR:"
        )

        print(
            error
        )

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

    application.add_handler(
        CommandHandler(
            "start",
            start
        )
    )

    application.add_handler(
        CallbackQueryHandler(
            button_handler
        )
    )

    application.add_handler(
        MessageHandler(
            filters.PHOTO,
            handle_photo
        )
    )

    application.add_handler(
        PreCheckoutQueryHandler(
            precheckout_callback
        )
    )

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


if __name__ == "__main__":

    main()
