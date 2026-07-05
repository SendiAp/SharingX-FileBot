import base64

from pyrogram import Client, filters

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

    except Exception:
        await message.reply_text("❌ Link tidak valid atau file tidak ditemukan.")

@Client.on_message(filters.private & ~filters.command("start"))
async def store_file(client, message):
    db_msg = await client.copy_message(
        chat_id=DATABASE_CHANNEL,
        from_chat_id=message.chat.id,
        message_id=message.id
    )

    data = f"get-{db_msg.id}"
    token = base64.urlsafe_b64encode(data.encode()).decode()

    link = f"https://t.me/{BOT_USERNAME}?start={token}"

    await message.reply_text(
        f"✅ Link Sharing File Berhasil Dibuat.\n\n{link}"
    )
