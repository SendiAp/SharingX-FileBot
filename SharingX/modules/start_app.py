import asyncio
import os
import importlib

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from SharingX import app, Bot
from SharingX.helper.database import add_bot
from SharingX.modules import loadModule

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):

    await message.reply_text(
        "<b>🤖 Welcome To SharingX Bot Manager</b>\n\n"
        "Silahkan pilih menu di bawah untuk membuat bot baru.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ Create Bot",
                        callback_data="create_bot"
                    )
                ]
            ]
        )
    )
  
@app.on_callback_query(filters.regex("create_bot"))
async def create_bot(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    callback = await callback_query.edit_message_text(
        "<b>🤖 Masukkan API ID Anda:</b>\n\n"
        "__Dapatkan di web [my.telegram.org](https://my.telegram.org)__"
    )

    while True:
        user_msg = await app.listen(user_id)

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
        "<b>🤖 Masukkan API HASH Anda:</b>\n\n"
        "__Dapatkan di web [my.telegram.org](https://my.telegram.org)__"
    )

    user_msg = await app.listen(user_id)

    api_hash = user_msg.text.strip()

    await user_msg.delete()


    await callback.edit(
        "<b>🤖 Masukkan BOT TOKEN Anda:</b>\n\n"
        "__Dapatkan di BOT @BotFather__"
    )

    user_msg = await app.listen(user_id)

    bot_token = user_msg.text.strip()

    await user_msg.delete()


    await callback.edit(
        "<b>🗄 Masukkan MongoDB URL:</b>\n\n"
        "Contoh:\n"
        "<code>mongodb+srv://user:pass@cluster.mongodb.net/</code>"
    )

    user_msg = await app.listen(user_id)

    mongo_url = user_msg.text.strip()

    await user_msg.delete()


    await callback.edit(
        "<b>📂 Masukkan Nama Database:</b>\n\n"
        "Default: <code>sharingx</code>"
    )

    user_msg = await app.listen(user_id)

    database = user_msg.text.strip()

    await user_msg.delete()


    if not database:
        database = "sharingx"


    await callback.edit(
        "<b>⏳ Mengecek data bot...</b>"
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
            f"<b>✅ Bot berhasil ditemukan!</b>\n\n"
            f"<b>• Nama:</b> {me.first_name}\n"
            f"<b>• Username:</b> @{me.username}\n\n"
            f"<b>⏳ Menyimpan konfigurasi...</b>"
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


    await asyncio.sleep(2)


    await callback.edit(
        "<b>✅ Bot Anda Berhasil Diaktifkan!</b>\n\n"
        f"<b>• Username:</b> @{me.username}\n"
        f"<b>• Database:</b> <code>{database}</code>",
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
                f"Media.modules.{mod}"
            )
        )


    try:
        os.popen(f"rm {bot_id}*")

    except:
        pass
