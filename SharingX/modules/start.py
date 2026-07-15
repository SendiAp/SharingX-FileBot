import base64

from pyrogram import Client, filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from SharingX import bot
from SharingX.helper.database import (
    set_link_status,
    get_link_status,
    set_database_channel,
    get_database_channel
)

@Client.on_message(filters.command("start"))
async def start(client, message):
    if len(message.command) < 2:
        return await message.reply_text("Kirim file untuk membuat link.")

    try:
        token = message.command[1]
        database_channel = await get_database_channel()
        data = base64.urlsafe_b64decode(token).decode()
        
        if data.startswith("get-"):
            msg_id = int(data.split("-")[1])

            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=database_channel,
                message_id=msg_id,
                reply_markup=None
            )

        elif data.startswith("batch-"):
            _, start_id, end_id = data.split("-")

            for msg_id in range(int(start_id), int(end_id) + 1):
                try:
                    await client.copy_message(
                        chat_id=message.chat.id,
                        from_chat_id=database_channel,
                        message_id=msg_id,
                        reply_markup=None
                    )
                except:
                    pass
        else:
            raise Exception()

    except Exception as e:
        await message.reply_text(
            f"<b>Terjadi Kesalahan:</b> <code>{str(e)}</code>"
        )

@Client.on_message(filters.command("link"))
async def link_mode(client, message):
    if len(message.command) != 2:
        status = await get_link_status()

        return await message.reply(
            f"<b>Status Auto Link:</b> "
            f"<code>{'ON' if status else 'OFF'}</code>\n\n"
            "<b>Penggunaan:</b>\n"
            "<code>/link on</code>\n"
            "<code>/link off</code>"
        )

    mode = message.command[1].lower()

    if mode == "on":
        await set_link_status(True)
        return await message.reply(
            "✅ Auto pembuatan link berhasil diaktifkan."
        )

    elif mode == "off":
        await set_link_status(False)
        return await message.reply(
            "🛑 Auto pembuatan link berhasil dinonaktifkan."
        )

    else:
        return await message.reply(
            "❌ Gunakan:\n"
            "<code>/link on</code>\n"
            "<code>/link off</code>"
        )
        
@Client.on_message(filters.command("batch") & filters.private)
async def batch(client, message):
    try:
        msg = await message.reply_text(
            "<b>🤖 Bot: Silahkan Kirim Link Awal Tautan Yang Ada Dipostingan Database Anda?</b>\n\n"
            "/cancel - Untuk Membatalkan!"
        )

        start_msg = await client.listen(message.chat.id)
        
        if start_msg.text and start_msg.text.startswith("/"):
            await start_msg.delete()
            return await msg.edit("<b>❌ Proses Dibatalkan!</b>")

        start = start_msg.text.strip()
        await start_msg.delete()
        
        msg = await msg.edit(
            "<b>🤖 Bot: Silahkan Kirim Link Akhir Tautan Yang Ada Dipostingan Database Anda?</b>\n\n"
            "/cancel - Untuk Membatalkan!"
        )

        end_msg = await client.listen(message.chat.id)
        
        if end_msg.text and end_msg.text.startswith("/"):
            await end_msg.delete()
            return await msg.edit("<b>❌ Proses Dibatalkan!</b>")

        end = end_msg.text.strip()
        await end_msg.delete()
        
        if start.isdigit():
            start_id = int(start)
        else:
            start_id = int(start.rstrip("/").split("/")[-1])

        if end.isdigit():
            end_id = int(end)
        else:
            end_id = int(end.rstrip("/").split("/")[-1])

        if start_id > end_id:
            return await msg.edit(
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

        await msg.edit(
            f"<b>Link Batch Berhasil Di Buat :</b>\n\n{link}",
            reply_markup=keyboard
        )

    except Exception as e:
        await message.reply_text(
            f"<b>Terjadi Kesalahan:</b>\n<code>{e}</code>"
        )

@Client.on_message(filters.command("adddb"))
async def adddb(client, message):
    chat_id = None

    if len(message.command) > 1:
        target = message.command[1]

        if target.startswith("@"):
            try:
                chat = await client.get_chat(target)
                chat_id = chat.id
            except Exception:
                return await message.reply(
                    "❌ Username channel/grup tidak ditemukan."
                )
        else:
            try:
                chat_id = int(target)
            except ValueError:
                return await message.reply(
                    "❌ Chat ID tidak valid."
                )

    elif message.reply_to_message:
        reply = message.reply_to_message

        if reply.forward_from_chat:
            chat_id = reply.forward_from_chat.id
        elif reply.sender_chat:
            chat_id = reply.sender_chat.id
        else:
            return await message.reply(
                "❌ Reply ke pesan hasil forward dari channel/grup."
            )

    else:
        return await message.reply(
            "<b>Gunakan salah satu cara berikut:</b>\n\n"
            "• <code>/adddb -100xxxxxxxxxx</code>\n"
            "• <code>/adddb @username</code>\n"
            "• Reply ke pesan hasil forward dari channel/grup dengan <code>/adddb</code>"
        )

    try:
        await client.send_message(
            chat_id,
            "✅ Berhasil disimpan sebagai Database Channel."
        )
    except Exception:
        return await message.reply(
            "❌ Bot tidak dapat mengirim pesan ke channel/grup.\n"
            "Pastikan bot sudah menjadi admin dan memiliki izin mengirim pesan."
        )

    await set_database_channel(chat_id)

    chat = await client.get_chat(chat_id)

    await message.reply(
        f"✅ Database berhasil disimpan.\n\n"
        f"<b>Nama:</b> {chat.title}\n"
        f"<b>Chat ID:</b> <code>{chat_id}</code>"
    )

@Client.on_message(filters.command("deldb"))
async def deldb(client, message):
    chat_id = await get_database_channel()

    if not chat_id:
        return await message.reply(
            "❌ Database Channel belum disetel."
        )

    try:
        chat = await client.get_chat(chat_id)
        name = chat.title
    except Exception:
        name = "Tidak diketahui"

    await del_database_channel()

    await message.reply(
        f"🗑 Database Channel berhasil dihapus.\n\n"
        f"<b>Nama:</b> {name}\n"
        f"<b>Chat ID:</b> <code>{chat_id}</code>"
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
    if not await get_link_status():
        return
        
    database_channel = await get_database_channel()
    if not database_channel:
        return await message.reply_text(
            "❌ Database Channel belum disetel.\nGunakan /adddb terlebih dahulu."
        )
        
    try:
        db_msg = await client.copy_message(
            chat_id=database_channel,
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
            chat_id=database_channel,
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
