async def successful_payment(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    photo_path = get_user_photo(user_id)

    if not photo_path:
        await update.message.reply_text(
            "✅ Оплата получена.\n\n"
            "Но фотография не найдена. Пожалуйста, отправьте её ещё раз."
        )
        return

    await update.message.reply_text(
        "✅ Оплата получена!\n\n"
        "🔎 Выполняю полный анализ..."
    )

    try:
        result = analyze_image(photo_path, full=True)

        await send_long_message(
            update.message,
            result
        )

        await update.message.reply_text(
            "🎨 Теперь подготавливаю улучшенную версию фотографии..."
        )

        improved_photo = generate_improved_photo(
            photo_path
        )

        with open(improved_photo, "rb") as photo_file:
            await update.message.reply_photo(
                photo=photo_file,
                caption="✨ Готово! Улучшенная версия фотографии."
            )

    except Exception as error:
        print("FULL ANALYSIS / IMAGE ERROR:")
        print(error)

        await update.message.reply_text(
            "❌ Не удалось обработать фотографию.\n\n"
            "Попробуйте ещё раз позже."
        )
