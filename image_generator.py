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
            "можно приобрести полный анализ.",
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

        # Короткий анализ
        result = analyze_image(temporary_path, full=False)
        add_free_analysis(user_id)

        await send_long_message(update.message, result)

        # Сразу создаём и отправляем улучшенную фотографию (бесплатно)
        await update.message.reply_text(
            "🎨 Создаю улучшенную версию фотографии..."
        )

        improved_photo = generate_improved_photo(temporary_path)

        with open(improved_photo, "rb") as photo_file:
            await update.message.reply_photo(
                photo=photo_file,
                caption=(
                    "✨ Готово!\n\n"
                    "Обработанная looksmaxxing-версия вашей фотографии."
                )
            )

        # Предложение купить полный анализ
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
            "этой фотографии с подробными рекомендациями?",
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
