import time
import asyncio

from datetime import datetime
from zoneinfo import ZoneInfo

from pyrogram import filters
from pyrogram.errors import (
    FloodWait,
    UserIsBlocked,
    InputUserDeactivated
)

from SharingX import Bot
from SharingX.modules.db import (
    get_user,
    del_user,
)

async def remove_duplicates(client, users):
    seen = set()
    unique_users = []

    for user_id in users:
        if user_id not in seen:
            seen.add(user_id)
            unique_users.append(user_id)
        else:
            await del_user(client, user_id)

    return unique_users

def format_duration(seconds):
    seconds = int(seconds)

    if seconds < 60:
        return f"{seconds} detik"

    if seconds < 3600:
        menit, detik = divmod(seconds, 60)

        if detik:
            return f"{menit} menit {detik} detik"

        return f"{menit} menit"

    jam, sisa = divmod(seconds, 3600)
    menit, detik = divmod(sisa, 60)

    result = f"{jam} jam"

    if menit:
        result += f" {menit} menit"

    if detik:
        result += f" {detik} detik"

    return result

@Bot.on_message(filters.command(["broadcast", "gcast"]))
async def broadcast(client, message):

    if not message.reply_to_message:
        return await message.reply(
            "<b>❌ Reply Pesan Yang Ingin Dibroadcast!</b>"
        )

    users = await get_user(client)

    if not users:
        return await message.reply(
            "⚠️ Tidak Ada Pengguna Yang Terdaftar!"
        )

    users = await remove_duplicates(
        client,
        users
    )

    broadcast_msg = message.reply_to_message

    total = len(users)
    successful = 0
    blocked = 0
    deleted = 0
    unsuccessful = 0

    timezone_wib = ZoneInfo("Asia/Jakarta")

    start_timestamp = time.time()

    start_datetime = datetime.now(
        timezone_wib
    ).strftime(
        "%d-%m-%Y %H:%M:%S WIB"
    )

    pls_wait = await message.reply(
        "📡 Broadcast Sedang Berlangsung..."
    )

    for user_id in users:

        try:
            await broadcast_msg.copy(user_id)
            successful += 1

        except FloodWait as e:
            await asyncio.sleep(e.value)

            try:
                await broadcast_msg.copy(user_id)
                successful += 1

            except Exception:
                unsuccessful += 1

        except UserIsBlocked:
            await del_user(
                client,
                user_id
            )
            blocked += 1

        except InputUserDeactivated:
            await del_user(
                client,
                user_id
            )
            deleted += 1

        except Exception:
            unsuccessful += 1

    end_timestamp = time.time()

    end_datetime = datetime.now(
        timezone_wib
    ).strftime(
        "%d-%m-%Y %H:%M:%S WIB"
    )

    duration = format_duration(
        end_timestamp - start_timestamp
    )

    status = (
        "<u>✅ ʙʀᴏᴀᴅᴄᴀsᴛ sᴜᴄᴄᴇss</u>\n"
        f"👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs: <code>{total}</code>\n"
        f"📩 ᴛᴇʀᴋɪʀɪᴍ: <code>{successful}</code>\n"
        f"❌ ᴛɪᴅᴀᴋ ᴛᴇʀᴋɪʀɪᴍ: <code>{unsuccessful}</code>\n"
        f"🚫 ʙʟᴏᴄᴋ ᴘᴇɴɢɢᴜɴᴀ: <code>{blocked}</code>\n"
        f"🗑️ ᴀᴋᴜɴ ᴛᴇʀʜᴀᴘᴜs: <code>{deleted}</code>\n"
        f"🕐 ᴡᴀᴋᴛᴜ ᴍᴜʟᴀɪ: <code>{start_datetime}</code>\n"
        f"🕐 ᴡᴀᴋᴛᴜ sᴇʟᴇsᴀɪ: <code>{end_datetime}</code>\n"
        f"⏱️ ᴅᴜʀᴀsɪ: <code>{duration}</code>"
    )

    await pls_wait.edit(status)
