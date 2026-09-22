import sys
import base64
import traceback
from zoneinfo import ZoneInfo
from datetime import datetime, timezone

from pyrogram import filters
from pyrogram.errors import FloodWait
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    Message
)

from SharingX import Bot
from SharingX.helper.database import botdb
from SharingX.helper.tools import strtobool, encode, decode, get_messages, get_message_id
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
    protect_info,
    add_protect,
    get_owners,
    get_admins,
    add_admin,
    del_admin,
    is_admin,
    is_owner,
    get_user,
    add_user
)


async def owner_admin_filter(_, client, message):
    user_id = message.from_user.id

    if await is_owner(client, user_id):
        return True

    if await is_admin(client, user_id):
        return True

    return False


owner_admin = filters.create(owner_admin_filter)


async def owner_filter(_, client, message):
    return await is_owner(client, message.from_user.id)


owner = filters.create(owner_filter)


@Bot.on_message(filters.command("adddb") & filters.private & owner_admin)
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
        forward_origin = reply.forward_origin

        if (
            forward_origin
            and hasattr(forward_origin, "chat")
            and forward_origin.chat
            and forward_origin.chat.sender_chat
        ):
            chat_id = forward_origin.chat.sender_chat.id

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
        await client.send_message(
            chat_id,
            "🔗 Connect, Channel/Groups Ini Berhasil Disimpan Untuk Database!"
        )
    except Exception:
        return await message.reply_text(
            "<b>⚠️ Bot Perlu Menjadi Admin!</b>"
        )

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


@Bot.on_message(filters.command("deldb") & filters.private & owner)
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


@Bot.on_message(filters.command(["addadmin", "aadmin"]) & filters.private & owner)
async def add_admin_cmd(client, message):
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        query = message.command[1].strip()

        if query.startswith("@"):
            query = query[1:]

        try:
            if query.isdigit():
                target = await client.get_users(int(query))
            else:
                target = await client.get_users(query)
        except Exception:
            return await message.reply("<b>❌ User tidak ditemukan.</b>")
    else:
        return await message.reply(
            "<b>Gunakan:</b>\n"
            "• Balas pesan dengan <code>/addadmin</code>\n"
            "• <code>/addadmin user_id</code>\n"
            "• <code>/addadmin @username</code>"
        )

    if target.id == message.from_user.id:
        return await message.reply("<b>❌ Anda tidak dapat menambahkan diri sendiri sebagai admin.</b>")

    if await is_owner(client, target.id):
        return await message.reply("<b>❌ Owner tidak dapat ditambahkan sebagai admin.</b>")

    if await is_admin(client, target.id):
        return await message.reply(
            f"<b>⚠️ {target.mention} sudah menjadi admin.</b>"
        )

    await add_admin(client, target.id)

    try:
        await client.send_message(
            target.id,
            "<b>🙌 Selamat! Anda telah ditambahkan sebagai Admin bot ini.</b>\n\n"
            "Gunakan /help untuk melihat daftar perintah yang tersedia."
        )
    except Exception:
        pass

    await message.reply(
        f"<b>✅ Berhasil menambahkan {target.mention} <code>({target.id})</code> sebagai admin.</b>"
    )


@Bot.on_message(filters.command(["deladmin", "rmadmin", "removeadmin"]) & filters.private & owner)
async def del_admin_cmd(client, message):
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        query = message.command[1].strip()

        if query.startswith("@"):
            query = query[1:]

        try:
            if query.isdigit():
                target = await client.get_users(int(query))
            else:
                target = await client.get_users(query)
        except Exception:
            return await message.reply("<b>❌ User tidak ditemukan.</b>")
    else:
        return await message.reply(
            "<b>Gunakan:</b>\n"
            "• Balas pesan dengan <code>/deladmin</code>\n"
            "• <code>/deladmin user_id</code>\n"
            "• <code>/deladmin @username</code>"
        )

    if await is_owner(client, target.id):
        return await message.reply("<b>❌ Owner tidak dapat dihapus dari admin.</b>")

    if not await is_admin(client, target.id):
        return await message.reply(
            f"<b>⚠️ {target.mention} bukan admin.</b>"
        )

    await del_admin(client, target.id)

    await message.reply(
        f"<b>✅ Berhasil menghapus {target.mention} <code>({target.id})</code> dari admin.</b>"
    )


@Bot.on_message(filters.command(["listadmin", "admins"]) & filters.private & owner)
async def list_admin_cmd(client, message):
    owners = await get_owners(client)
    admins = await get_admins(client)

    text = "<b>👥 Daftar Admin Bot</b>\n\n"

    if owners:
        text += "<b>👑 Owner:</b>\n"

        for i, user_id in enumerate(owners, 1):
            try:
                user = await client.get_users(user_id)
                text += f"{i}. 👑 {user.mention} <code>({user.id})</code>\n"
            except Exception:
                text += f"{i}. 👑 <code>{user_id}</code>\n"

    if admins:
        text += "\n<b>🛡 Admin:</b>\n"

        for i, user_id in enumerate(admins, 1):
            try:
                user = await client.get_users(user_id)
                text += f"{i}. 🛡 {user.mention} <code>({user.id})</code>\n"
            except Exception:
                text += f"{i}. 🛡 <code>{user_id}</code>\n"
    else:
        text += "\n<i>Belum ada admin.</i>"

    await message.reply(text)


@Bot.on_message(
    filters.private
    & ~filters.command("start", "batch")
    & owner_admin
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

        fuck = db_msg.id * abs(database_channel)
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

@Bot.on_message(filters.command("genlink") & filters.private & owner_admin)
async def genlink(client, message):

    while True:
        try:
            target_message = await client.ask(
                message.from_user.id,
                "<b>Silahkan Kirim Link Postingan dari Channel Database.</b>",
                filters=filters.text & ~filters.command
            )
        except BaseException:
            return

        if target_message.text and target_message.text.startswith("/"):
            await target_message.delete()
            return await message.reply(
                "<b>❌ Proses dibatalkan.</b>"
            )

        msg_id = await get_message_id(
            client,
            target_message
        )

        if msg_id:
            break

        await target_message.reply(
            "❌ <b>ERROR</b>\n\n"
            "<b>Link yang dikirim bukan dari Channel Database saya.</b>"
        )

    database_channel = await get_database_channel(client)

    if not database_channel:
        return await message.reply(
            "<b>⚠️ Tidak Ada Channel/Groups Database Yang Terhubung!</b>"
        )

    chg = abs(database_channel)

    string = f"get-{msg_id * chg}"
    token = await encode(string)

    me = client.me or await client.get_me()

    link = f"https://t.me/{me.username}?start={token}"

    reply_markup = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "Copy Link",
                    copy_text=link
                )
            ]
        ]
    )

    await target_message.reply_text(
        f"<b>Link Sharing File Berhasil Di Buat:</b>\n\n{link}",
        reply_markup=reply_markup
    )
