@app.on_callback_query(filters.regex("create_bot"))
async def create_bot(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    callback = await callback_query.edit_message_text(
        "<b>🤖 Bot:</b> Masukkan API ID Anda?\n\n"
        "__Dapatkan di web [my.telegram.org](https://my.telegram.org)__\n\n"
        "Tahap <pre>1/5</pre>\n\n"
        "/cancel - Untuk Membatalkan!"
    )

    while True:
        user_msg = await app.listen(user_id)

        if user_msg.text and user_msg.text.startswith("/"):
            await user_msg.delete()
            await callback.edit(
                "<b>❌ Pembuatan Bot Dibatalkan.</b>",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "🔙 Kembali",
                            callback_data="my_bots"
                        )
                    ]
                ])
            )
            return
            
        try:
            api_id = int(user_msg.text)
            await user_msg.delete()
            break

        except ValueError:
            await user_msg.delete()

            warn = await client.send_message(
                user_id,
                "<b>⚠️ API ID harus berupa angka!</b>"
            )

            await asyncio.sleep(2)
            await warn.delete()

    await callback.edit(
        "<b>🤖 Bot:</b> Masukkan API HASH Anda?\n\n"
        "__Dapatkan di web [my.telegram.org](https://my.telegram.org)__\n\n"
        "Tahap <pre>2/5</pre>\n\n"
        "/cancel - Untuk Membatalkan!"
    )

    user_msg = await app.listen(user_id)
    
    if user_msg.text and user_msg.text.startswith("/"):
        await user_msg.delete()
        await callback.edit(
            "<b>❌ Pembuatan Bot Dibatalkan.</b>",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 Kembali",
                        callback_data="my_bots"
                    )
                ]
            ])
        )
        return
        
    api_hash = user_msg.text.strip()

    await user_msg.delete()

    await callback.edit(
        "<b>🤖 Bot:</b> Masukkan BOT TOKEN Anda?\n\n"
        "__Dapatkan di BOT @BotFather__\n\n"
        "Tahap <pre>3/5</pre>\n\n"
        "/cancel - Untuk Membatalkan!"
    )

    user_msg = await app.listen(user_id)

    if user_msg.text and user_msg.text.startswith("/"):
        await user_msg.delete()
        await callback.edit(
            "<b>❌ Pembuatan Bot Dibatalkan.</b>",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 Kembali",
                        callback_data="my_bots"
                    )
                ]
            ])
        )
        return
        
    bot_token = user_msg.text.strip()

    await user_msg.delete()

    await callback.edit(
        "<b>🤖 Bot:</b> Masukkan MongoDB URL Anda?\n\n"
        "__Contoh: mongodb+srv://user:pass@cluster.mongodb.net/__\n\n"
        "Tahap <pre>4/5</pre>\n\n"
        "/cancel - Untuk Membatalkan!"
    )

    user_msg = await app.listen(user_id)
    
    if user_msg.text and user_msg.text.startswith("/"):
        await user_msg.delete()
        await callback.edit(
            "<b>❌ Pembuatan Bot Dibatalkan.</b>",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 Kembali",
                        callback_data="my_bots"
                    )
                ]
            ])
        )
        return
        
    mongo_url = user_msg.text.strip()

    await user_msg.delete()

    await callback.edit(
        "<b>🤖 Bot:</b> Masukkan Nama Database?\n\n"
        "Default: <code>sharingx</code>\n\n"
        "Tahap <pre>5/5</pre>\n\n"
        "/cancel - Untuk Membatalkan!"
    )

    user_msg = await app.listen(user_id)

    if user_msg.text and user_msg.text.startswith("/"):
        await user_msg.delete()
        await callback.edit(
            "<b>❌ Pembuatan Bot Dibatalkan.</b>",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 Kembali",
                        callback_data="my_bots"
                    )
                ]
            ])
        )
        return
        
    database = user_msg.text.strip()

    await user_msg.delete()

    if not database:
        database = "sharingx"

    await callback.edit(
        "<b>⏳ Sedang Melihat Data Bot, Mohon Tunggu...</b>"
    )

    bot_id = bot_token.split(":")[0]

    media = Bot(
        name=str(bot_id),
        api_id=api_id,
        api_hash=api_hash,
        bot_token=bot_token
    )

    try:
        media.in_memory = False

        await media.start()

        me = await media.get_me()

        await callback.edit(
            f"<b>✅ Bot Berhasil Ditemukan!</b>\n\n"
            f"<b>• Nama:</b> {me.first_name}\n"
            f"<b>• Username:</b> @{me.username}\n\n"
            f"<b>⏳ Menyimpan Konfigurasi...</b>"
        )

    except Exception as e:

        error = str(e)

        if "ACCESS_TOKEN_INVALID" in error:
            return await callback.edit(
                "<b>⚠️ BOT TOKEN TIDAK VALID</b>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "➕ Mulai Lagi",
                                callback_data="create_bot"
                            )
                        ]
                    ]
                )
            )


        if "API_ID_INVALID" in error:
            return await callback.edit(
                "<b>⚠️ API ID / API HASH TIDAK VALID</b>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "➕ Mulai Lagi",
                                callback_data="create_bot"
                            )
                        ]
                    ]
                )
            )


        return await callback.edit(
            f"<b>❌ ERROR:</b>\n<code>{error}</code>"
        )

    await add_bot(
        str(media.me.id),
        api_id,
        api_hash,
        bot_token,
        mongo_url,
        database
    )

    await add_user_bot(
        user_id,
        str(me.id)
    )

    await add_owner(
        str(me.id),
        user_id
    )

    await add_reminder(
        str(media.me.id),
        4
    )
    
    await remove_bot_space(
        user_id,
        1
    )
    
    await asyncio.sleep(2)
    
    await callback.edit(
        "<b>✅ Bot Anda Berhasil Disimpan!</b>\n\n"
        f"<b>• Username:</b> @{me.username}\n"
        f"<b>• Database:</b> <code>{database}</code>\n\n"
        "__Untuk Melihat Status Bot Anda Silahkan Pergi Ke Start Dibot Ini.__",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"@{me.username}",
                        url=f"https://t.me/{me.username}"
                    )
                ]
            ]
        )
    )

    for mod in loadModule():
        importlib.reload(
            importlib.import_module(
                f"SharingX.modules.{mod}"
            )
        )
        
    try:
        os.popen(f"rm {bot_id}*")
    except:
        pass
        
    os.execv(
        sys.executable,
        [sys.executable, "-m", "SharingX"]
    )
