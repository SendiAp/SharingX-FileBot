import base64

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from SharingX import bot

DATABASE_CHANNEL = -1004437744973


@Client.on_message(filters.command("start"))
async def start(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Kirim file untuk membuat link.")

    try:
        token = message.command[1]
        data = base64.urlsafe_b64decode(token).decode()

        if data.startswith("get-"):
            msg_id = int(data.split("-")[1])

            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=DATABASE_CHANNEL,
                message_id=msg_id
            )

        elif data.startswith("batch-"):
            _, start_id, end_id = data.split("-")

            for msg_id in range(int(start_id), int(end_id) + 1):
                try:
                    await client.copy_message(
                        chat_id=message.chat.id,
                        from_chat_id=DATABASE_CHANNEL,
                        message_id=msg_id
                    )
                except:
                    pass
        else:
            raise Exception()

    except Exception as e:
        await message.reply_text(
            f"<b>Terjadi Kesalahan:</b> <code>{str(e)}</code>"
        )


@Client.on_message(filters.command("batch") & filters.private)
async def batch(client, message):
    try:
        if len(message.command) != 3:
            return await message.reply_text(
                "<b>Penggunaan:</b>\n<code>/batch link_awal link_akhir</code>"
            )

        start = message.command[1]
        end = message.command[2]

        if start.isdigit():
            start_id = int(start)
        else:
            start_id = int(start.rstrip("/").split("/")[-1])

        if end.isdigit():
            end_id = int(end)
        else:
            end_id = int(end.rstrip("/").split("/")[-1])

        if start_id > end_id:
            return await message.reply_text(
                "<b>ID awal harus lebih kecil dari ID akhir.</b>"
            )

        data = f"batch-{start_id}-{end_id}"
        token = base64.urlsafe_b64encode(data.encode()).decode()

        username = (await client.get_me()).username
        link = f"https://t.me/{username}?start={token}"

        keyboard = InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "Copy Link",
                    copy_text=link
                )
            ]
        ])

        await message.reply_text(
            f"<b>Batch Link Berhasil Di Buat :</b>\n\n{link}",
            reply_markup=keyboard
        )

    except Exception as e:
        await message.reply_text(
            f"<b>Terjadi Kesalahan:</b>\n<code>{str(e)}</code>"
        )


@Client.on_message(
    filters.private
    & ~filters.command("start", "batch")
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
                    "Copy Link",
                    copy_text=link
                )
            ]
        ])

        await client.edit_message_reply_markup(
            chat_id=DATABASE_CHANNEL,
            message_id=db_msg.id,
            reply_markup=keyboard
        )

        await message.reply_text(
            f"<b>Link Sharing File Berhasil Di Buat :</b>\n\n{link}",
            reply_markup=keyboard
        )

    except Exception as e:
        await message.reply_text(
            f"<b>Terjadi Kesalahan:</b>\n<code>{str(e)}</code>"
        )
