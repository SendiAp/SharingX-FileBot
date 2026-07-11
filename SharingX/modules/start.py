import base64

from pyrogram import Client, filters

from SharingX import bot

DATABASE_CHANNEL = -1004437744973

@Client.on_message(filters.command("start"))
async def start(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Kirim file untuk membuat link.")

    try:
        token = message.command[1]
        data = base64.urlsafe_b64decode(token).decode()

        if not data.startswith("get-"):
            raise Exception()

        msg_id = int(data.split("-")[1])

        await client.copy_message(
            chat_id=message.chat.id,
            from_chat_id=DATABASE_CHANNEL,
            message_id=msg_id
        )

    except Exception as e:
        await message.reply_text(
            f"<b>Terjadi Kesalahan:</b> `{str(e)}`"
        )

@Client.on_message(
    filters.private
    & ~filters.command("start")
    & (
        filters.photo
        | filters.text
        | filters.video
        | filters.document
        | filters.audio
        | filters.voice
        | filters.video_note
        | filters.animation
        | filters.sticker
    )
)
async def store_file(client, message):
    try:
        db_msg = await client.copy_message(
            chat_id=DATABASE_CHANNEL,
            from_chat_id=message.chat.id,
            message_id=message.id
        )

        data = f"get-{db_msg.id}"
        token = base64.urlsafe_b64encode(data.encode()).decode()

        username = (await client.get_me()).username
        link = f"https://t.me/{username}?start={token}"

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "📋 Copy Link",
                    copy_text=link
                )
            ]
        ])

        await message.reply_text(
            f"✅ Link Sharing File Berhasil Dibuat.\n\n{link}",
            reply_markup=keyboard
        )

    except Exception as e:
        await message.reply_text(
            f"<b>Terjadi Kesalahan:</b>\n<code>{str(e)}</code>"
        )
