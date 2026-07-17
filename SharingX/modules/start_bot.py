import base64

from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
)

from SharingX import Bot
from SharingX.modules.db import (
    get_forcesub_button_mode,
    set_database_channel,
    get_database_channel,
    del_database_channel,
    set_link_status,
    get_link_status,
    add_forcesub,
    get_forcesubs,
    del_forcesub,
    get_user,
    add_user
)

async def encode(text: str):
    return base64.urlsafe_b64encode(
        text.encode()
    ).decode().rstrip("=")

async def decode(text: str):
    text += "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(
        text.encode()
    ).decode()
    
@Bot.on_message(filters.command("start") & filters.private)
async def start(client, message):

    users = await get_user(client)
    if message.from_user.id not in users:
        await add_user(client, message.from_user.id)

    if len(message.command) < 2:

        forcesubs = await get_forcesubs(client)
        mode = await get_forcesub_button_mode(client)

        buttons, row = [], []

        for chat_id in forcesubs:
            try:
                chat = await client.get_chat(chat_id)

                if chat.username:
                    url = f"https://t.me/{chat.username}"
                else:
                    invite = chat.invite_link
                    if not invite:
                        try:
                            invite = await client.create_chat_invite_link(chat.id)
                            invite = invite.invite_link
                        except:
                            continue
                    url = invite

                if mode == "text":
                    text = (
                        "Join Channel"
                        if chat.type.name.lower() == "channel"
                        else "Join Groups"
                    )
                elif mode == "username":
                    text = f"@{chat.username}" if chat.username else "Join"
                else:
                    text = chat.title

                row.append(
                    InlineKeyboardButton(text, url=url)
                )

                if len(row) == 2:
                    buttons.append(row)
                    row = []

            except:
                pass

        if row:
            buttons.append(row)

        if not buttons:
            buttons = [[
                InlineKeyboardButton(
                    "Tutup",
                    callback_data="close"
                )
            ]]

        return await message.reply_text(
            "<b>📁 Kirim file ke bot ini untuk membuat Link Sharing.</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    try:
        token = message.command[1]

        database_channel = await get_database_channel(client)

        if not database_channel:
            return await message.reply_text(
                "<b>⚠️ Tidak Ada Channel/Groups Database Yang Terhubung!</b>"
            )

        chg = abs(database_channel)

        data = await decode(token)

        if data.startswith("get-"):

            msg_id = int(data.split("-")[1]) // chg

            await client.copy_message(
                chat_id=message.chat.id,
                from_chat_id=database_channel,
                message_id=msg_id,
                reply_markup=None
            )

        elif data.startswith("batch-"):

            _, start_id, end_id = data.split("-")

            start_id = int(start_id) // chg
            end_id = int(end_id) // chg

            for msg_id in range(start_id, end_id + 1):
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
            raise Exception("⚠️ Link Tidak Valid!")

    except Exception as e:
        await message.reply_text(
            f"<b>Terjadi Kesalahan:</b>\n<code>{str(e)}</code>"
        )
        
@Bot.on_callback_query(filters.regex("^close$"))
async def close_callback(client, callback_query):
    try:
        await callback_query.message.delete()
        await callback_query.answer()
    except Exception as e:
        return await callback_query.edit_message_text(f"<b>Terjadi Kesalahan:</b> `{str(e)}`")
    
@Bot.on_message(filters.command("link") & filters.private)
async def link_mode(client, message):

    if len(message.command) != 2:

        status = await get_link_status(client)

        return await message.reply_text(
            f"<b>Status Auto Link :</b> "
            f"<code>{'ON' if status else 'OFF'}</code>\n\n"
            "<b>Penggunaan :</b>\n"
            "<code>/link on</code>\n"
            "<code>/link off</code>"
        )

    mode = message.command[1].lower()

    if mode == "on":

        await set_link_status(client, True)

        return await message.reply_text(
            "<b>🟢 Auto Link Berhasil Diaktifkan!</b>"
        )

    elif mode == "off":

        await set_link_status(client, False)

        return await message.reply_text(
            "<b>🛑 Auto Link Berhasil Dinonaktifkan!</b>"
        )

    else:
        
        return await message.reply_text(
            "<b>Gunakan:</b>\n"
            "<code>/link on</code>\n"
            "<code>/link off</code>"
        )

@Bot.on_message(filters.command("batch") & filters.private)
async def batch(client, message):
    try:
        msg = await message.reply_text(
            "<b>🤖 Silahkan kirim Link Awal dari Database Channel Anda.</b>\n\n"
            "/cancel - Untuk membatalkan."
        )

        first = await client.listen(message.chat.id)

        if not first or not first.text:
            return await msg.edit("<b>❌ Input tidak valid.</b>")

        if first.text.startswith("/"):
            await client.delete_messages(message.chat.id, first.id)
            return await msg.edit("<b>❌ Proses dibatalkan.</b>")

        start_link = first.text.strip()
        await client.delete_messages(message.chat.id, first.id)

        await msg.edit(
            "<b>🤖 Silahkan kirim Link Akhir dari Database Channel Anda.</b>\n\n"
            "/cancel - Untuk membatalkan."
        )

        second = await client.listen(message.chat.id)

        if not second or not second.text:
            return await msg.edit("<b>❌ Input tidak valid.</b>")

        if second.text.startswith("/"):
            await client.delete_messages(message.chat.id, second.id)
            return await msg.edit("<b>❌ Proses dibatalkan.</b>")

        end_link = second.text.strip()
        await client.delete_messages(message.chat.id, second.id)

        start_id = (
            int(start_link)
            if start_link.isdigit()
            else int(start_link.rstrip("/").split("/")[-1])
        )

        end_id = (
            int(end_link)
            if end_link.isdigit()
            else int(end_link.rstrip("/").split("/")[-1])
        )

        if start_id > end_id:
            return await msg.edit(
                "<b>❌ ID awal harus lebih kecil dari ID akhir.</b>"
            )

        db_channel = await get_database_channel(client)
        chg = abs(db_channel)
        
        string = f"batch-{start_id * chg}-{end_id * chg}"
        token = await encode(string)
        
        me = client.me or await client.get_me()
        link = f"https://t.me/{me.username}?start={token}"

        await msg.edit(
            f"<b>✅ Link Batch Berhasil Dibuat</b>\n\n{link}",
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "Copy Link",
                        copy_text=link
                    )
                ]
            ])
        )

    except Exception as e:
        await message.reply_text(
            f"<b>Terjadi Kesalahan:</b>\n<code>{str(e)}</code>"
        )
        
@Bot.on_message(filters.command("adddb") & filters.private)
async def adddb(client, message):

    chat_id = None

    if len(message.command) > 1:

        target = message.command[1]

        if target.startswith("@"):

            try:
                chat = await client.get_chat(target)
                chat_id = chat.id

            except Exception as e:
                return await message.reply_text(
                    f"<b>⚠️ Channel/Groups Tidak Ditemukan!</b>\n\n`{str(e)}`"
                )

        else:

            try:
                chat_id = int(target)

            except ValueError:
                return await message.reply_text("<b>❌ ID Tidak Valid!</b>")

    elif message.reply_to_message:

        reply = message.reply_to_message

        if reply.forward_from_chat:
            chat_id = reply.forward_from_chat.id

        elif reply.sender_chat:
            chat_id = reply.sender_chat.id

        else:
            return await message.reply_text(
                "<b>❌ Reply Ke Pesan Channel/Groups Hasil Forward!</b>"
            )

    else:

        return await message.reply_text(
            "<b>Gunakan salah satu cara berikut:</b>\n\n"
            "• <code>/adddb -100xxxxxxxxxx</code>\n"
            "• <code>/adddb @username</code>\n"
            "• Reply pesan hasil forward dari channel/grup dengan <code>/adddb</code>"
        )

    try:
        await client.send_message(chat_id, "🔗 Connect, Channel/Groups Ini Berhasil Disimpan Untuk Database!")
    except Exception:
        return await message.reply_text("<b>⚠️ Bot Perlu Menjadi Admin!</b>")

    await set_database_channel(client, chat_id)

    try:
        chat = await client.get_chat(chat_id)
        title = chat.title
    except:
        title = "Unknown"

    await message.reply_text(
        f"<b>✅ Channel/Groups Database Berhasil Disimpan!</b>\n\n"
        f"<b>Nama:</b> {title}\n"
        f"<b>ChatID:</b> <code>{chat_id}</code>"
    )

@Bot.on_message(filters.command("deldb") & filters.private)
async def deldb(client, message):

    chat_id = await get_database_channel(client)

    if not chat_id:
        return await message.reply_text("<b>⚠️ Tidak Ada Channel/Groups Database Yang Terhubung!</b>")

    try:
        chat = await client.get_chat(chat_id)
        name = chat.title
    except Exception:
        name = "Unknwon"

    await del_database_channel(client)

    await message.reply_text(
        f"<b>🗑 Groups/Channel Database Berhasil Dihapus!</b>\n\n"
        f"<b>Nama:</b> {name}\n"
        f"<b>ChatID:</b> <code>{chat_id}</code>"
    )

@Bot.on_message(
    filters.private
    & ~filters.command("start", "batch")
    & (
        filters.photo
        | filters.video
        | filters.document
        | filters.audio
        | filters.voice
        | filters.animation
        | filters.video_note
        | filters.sticker
        | filters.text
    )
)
async def store_file(client, message):

    if not await get_link_status(client):
        return

    database_channel = await get_database_channel(client)

    if not database_channel:
        return await message.reply_text(
            "<b>⚠️ Tidak Ada Channel/Groups Database Yang Terhubung!</b>"
        )

    try:

        db_msg = await client.copy_message(
            chat_id=database_channel,
            from_chat_id=message.chat.id,
            message_id=message.id
        )

        ids = await message.copy(database_channel)
        fuck = ids.id * abs(database_channel)
        string = f"get-{fuck}"
        token = await encode(string)

        me = await client.get_me()

        link = (
            f"https://t.me/{me.username}"
            f"?start={token}"
        )

        keyboard = InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "Copy Link",
                        copy_text=link
                    )
                ]
            ]
        )

        await client.edit_message_reply_markup(
            chat_id=database_channel,
            message_id=db_msg.id,
            reply_markup=keyboard
        )

        await message.reply_text(
            f"<b>✅ Link Sharing Berhasil Dibuat</b>\n\n{link}",
            reply_markup=keyboard
        )

    except Exception as e:

        await message.reply_text(
            f"<b>Terjadi Kesalahan:</b> <code>`{str(e)}`</code>"
    )
