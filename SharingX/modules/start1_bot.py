import asyncio
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
            f"ʜᴇʟʟᴏ {message.from_user.mention}\n\n"
            f"<b>sᴀʏᴀ ᴅᴀᴘᴀᴛ ᴍᴇɴʏɪᴍᴘᴀɴ ғɪʟᴇ ᴘʀɪʙᴀᴅɪ ᴅɪ ᴄʜᴀɴɴᴇʟ ᴛᴇʀᴛᴇɴᴛᴜ ᴅᴀɴ ᴘᴇɴɢɢᴜɴᴀ ʟᴀɪɴ ᴅᴀᴘᴀᴛ ᴍᴇɴɢᴀᴋsᴇsɴʏᴀ ᴅᴀʀɪ ʟɪɴᴋ ᴋʜᴜsᴜs.</b>",
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    try:
        token = message.command[1]

        if token == "start":
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
                f"ʜᴇʟʟᴏ {message.from_user.mention}\n\n"
                f"<b>sᴀʏᴀ ᴅᴀᴘᴀᴛ ᴍᴇɴʏɪᴍᴘᴀɴ ғɪʟᴇ ᴘʀɪʙᴀᴅɪ ᴅɪ ᴄʜᴀɴɴᴇʟ ᴛᴇʀᴛᴇɴᴛᴜ ᴅᴀɴ ᴘᴇɴɢɢᴜɴᴀ ʟᴀɪɴ ᴅᴀᴘᴀᴛ ᴍᴇɴɢᴀᴋsᴇsɴʏᴀ ᴅᴀʀɪ ʟɪɴᴋ ᴋʜᴜsᴜs.</b>",
                reply_markup=InlineKeyboardMarkup(buttons)
            )

        database_channel = await get_database_channel(client)

        if not database_channel:
            return await message.reply_text(
                "<b>⚠️ Tidak Ada Channel/Groups Database Yang Terhubung!</b>"
            )

        chg = abs(database_channel)

        data = await decode(token)

        cckh = await protect_info(client)

        rkhw = strtobool(cckh)

        if data.startswith("get-"):

            argument = data.split("-")

            if len(argument) == 2:

                msg_id = int(int(argument[1]) / abs(chg))

                try:
                    await client.copy_message(
                        chat_id=message.chat.id,
                        from_chat_id=database_channel,
                        message_id=msg_id,
                        protect_content=rkhw,
                        reply_markup=None
                    )

                except FloodWait as e:
                    await asyncio.sleep(e.value)

                    await client.copy_message(
                        chat_id=message.chat.id,
                        from_chat_id=database_channel,
                        message_id=msg_id,
                        protect_content=rkhw,
                        reply_markup=None
                    )

            elif len(argument) == 3:

                start = int(int(argument[1]) / abs(chg))
                end = int(int(argument[2]) / abs(chg))

                if start <= end:
                    ids = range(start, end + 1)
                else:
                    ids = []
                    i = start

                    while True:
                        ids.append(i)
                        i -= 1

                        if i < end:
                            break

                mes = await get_messages(
                    client,
                    list(ids),
                    database_channel
                )

                for msg in mes:
                    try:
                        await msg.copy(
                            message.chat.id,
                            protect_content=rkhw,
                            reply_markup=None
                        )

                    except FloodWait as e:
                        await asyncio.sleep(e.value)

                        await msg.copy(
                            message.chat.id,
                            protect_content=rkhw,
                            reply_markup=None
                        )

                    except:
                        pass

            else:
                raise Exception("⚠️ Link Tidak Valid!")

        elif data.startswith("batch-"):

            _, start_id, end_id = data.split("-")

            start_id = int(int(start_id) / abs(chg))
            end_id = int(int(end_id) / abs(chg))

            if start_id <= end_id:
                ids = range(start_id, end_id + 1)
            else:
                ids = []
                i = start_id

                while True:
                    ids.append(i)
                    i -= 1

                    if i < end_id:
                        break

            mes = await get_messages(
                client,
                list(ids),
                database_channel
            )

            for msg in mes:
                try:
                    await msg.copy(
                        message.chat.id,
                        protect_content=rkhw,
                        reply_markup=None
                    )
                except FloodWait as e:
                    await asyncio.sleep(e.value)

                    await msg.copy(
                        message.chat.id,
                        protect_content=rkhw,
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

@Bot.on_message(
    filters.command("stats") & filters.private & owner
)
async def stats(client, message):

    users = await get_user(
        client
    )

    total_user = len(
        set(users or [])
    )

    bot_id = str(
        client.me.id
    )

    data = botdb.find_one({
        "bot_id": bot_id
    })

    expired_text = "-"
    remaining_text = "-"
    terminated_text = "-"

    now = datetime.now(
        timezone.utc
    )

    if data:

        expires_at = data.get(
            "expires_at"
        )

        grace_until = data.get(
            "grace_until"
        )

        if expires_at:

            if expires_at.tzinfo is None:
                expires_at = expires_at.replace(
                    tzinfo=timezone.utc
                )
            else:
                expires_at = expires_at.astimezone(
                    timezone.utc
                )

            expired_text = expires_at.astimezone(
                ZoneInfo("Asia/Jakarta")
            ).strftime(
                "%d-%m-%Y %H:%M"
            )

            remaining = (
                expires_at - now
            )

            if remaining.total_seconds() > 0:

                total_seconds = int(
                    remaining.total_seconds()
                )

                days, remainder = divmod(
                    total_seconds,
                    86400
                )

                hours, remainder = divmod(
                    remainder,
                    3600
                )

                minutes, seconds = divmod(
                    remainder,
                    60
                )

                remaining_text = (
                    f"{days} Hari "
                    f"{hours} Jam "
                    f"{minutes} Menit "
                    f"{seconds} Detik"
                )

            else:
                remaining_text = "Expired"

        if grace_until:

            if grace_until.tzinfo is None:
                grace_until = grace_until.replace(
                    tzinfo=timezone.utc
                )
            else:
                grace_until = grace_until.astimezone(
                    timezone.utc
                )

            terminated_text = grace_until.astimezone(
                ZoneInfo("Asia/Jakarta")
            ).strftime(
                "%d-%m-%Y %H:%M"
            )

    text = (
        "<b>📊 Statistics</b>\n\n"
        f"<b>Total User :</b> "
        f"<code>{total_user}</code>\n"
        f"<b>Expired :</b> "
        f"<code>{expired_text}</code>\n"
        f"<b>Remaining :</b> "
        f"<code>{remaining_text}</code>\n"
        f"<b>Terminated :</b> "
        f"<code>{terminated_text}</code>"
    )

    await message.reply_text(
        text
    )

@Bot.on_callback_query(filters.regex("^close$"))
async def close_callback(client, callback_query):
    try:
        await callback_query.message.delete()
        await callback_query.answer()
    except Exception as e:
        return await callback_query.edit_message_text(f"<b>Terjadi Kesalahan:</b> `{str(e)}`")

@Bot.on_message(filters.command("link") & filters.private & owner_admin)
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

@Bot.on_message(filters.command("protect") & filters.private & owner_admin)
async def protect_cmd(client, message: Message):
    if len(message.command) != 2:
        return await message.reply_text(
            "<b>Usage:</b>\n"
            "<code>/protect true</code>\n"
            "<code>/protect false</code>"
        )

    value = message.command[1].lower()

    if value not in ("true", "false"):
        return await message.reply_text(
            "<b>Parameter harus:</b> <code>true</code> atau <code>false</code>"
        )

    protect = value == "true"

    await add_protect(client, protect)

    await message.reply_text(
        f"✅ <b>Protect berhasil {'diaktifkan' if protect else 'dinonaktifkan'}.</b>"
    )

@Bot.on_message(filters.command("batch") & filters.private & owner_admin)
async def batch(client, message):
    while True:
        try:
            first_message = await client.ask(
                message.from_user.id,
                "<b>Silahkan Teruskan Pesan/File Pertama dari Channel Database. (Forward with Qoute)</b>\n\n<b>atau Kirim Link Postingan dari Channel Database</b>",
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except BaseException:
            return

        if first_message.text and first_message.text.startswith("/"):
            await first_message.delete()
            return await message.reply(
                "<b>❌ Proses dibatalkan.</b>"
            )

        f_msg_id = await get_message_id(
            client,
            first_message
        )

        if f_msg_id:
            break

        await first_message.reply(
            "❌ <b>ERROR</b>\n\n<b>Postingan yang Diforward ini bukan dari Channel Database saya</b>"
        )

    while True:
        try:
            second_message = await client.ask(
                message.from_user.id,
                "<b>Silahkan Teruskan Pesan/File Terakhir dari Channel DataBase. (Forward with Qoute)</b>\n\n<b>atau Kirim Link Postingan dari Channel Database</b>",
                filters=(filters.forwarded | (filters.text & ~filters.forwarded)),
                timeout=60,
            )
        except BaseException:
            return

        if second_message.text and second_message.text.startswith("/"):
            await second_message.delete()
            return await message.reply(
                "<b>❌ Proses dibatalkan.</b>"
            )

        s_msg_id = await get_message_id(
            client,
            second_message
        )

        if s_msg_id:
            break

        await second_message.reply(
            "❌ <b>ERROR</b>\n\n<b>Postingan yang Diforward ini bukan dari Channel Database saya</b>"
        )

    database_channel = await get_database_channel(client)

    if not database_channel:
        return await message.reply(
            "<b>⚠️ Tidak Ada Channel/Groups Database Yang Terhubung!</b>"
        )

    chg = abs(database_channel)

    string = f"get-{f_msg_id * chg}-{s_msg_id * chg}"
    base64_string = await encode(string)

    me = client.me or await client.get_me()

    link = f"https://t.me/{me.username}?start={base64_string}"

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

    await second_message.reply_text(
        f"<b>Link Sharing File Berhasil Di Buat:</b>\n\n{link}",
        reply_markup=reply_markup
    )
