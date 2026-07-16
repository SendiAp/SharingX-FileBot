import time
import asyncio

from pyrogram import filters
from pyrogram.errors import (
    FloodWait,
    UserIsBlocked,
    InputUserDeactivated
)

from SharingX import Bot

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

    users = await remove_duplicates(client, users)

    broadcast_msg = message.reply_to_message

    total = len(users)
    successful = 0
    blocked = 0
    deleted = 0
    unsuccessful = 0

    start_time = time.time()

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
            await del_user(client, user_id)
            blocked += 1

        except InputUserDeactivated:
            await del_user(client, user_id)
            deleted += 1

        except Exception:
            unsuccessful += 1

    elapsed = int(time.time() - start_time)

    jam, sisa = divmod(elapsed, 3600)
    menit, detik = divmod(sisa, 60)

    await pls_wait.edit(
        "<b>✅ Broadcast Selesai</b>\n\n"
        f"👥 Total User : <code>{total}</code>\n"
        f"📨 Berhasil : <code>{successful}</code>\n"
        f"❌ Gagal : <code>{unsuccessful}</code>\n"
        f"🚫 Diblokir : <code>{blocked}</code>\n"
        f"🗑 Akun Terhapus : <code>{deleted}</code>\n"
        f"⏱ Waktu : <code>{jam:02}:{menit:02}:{detik:02}</code>"
    )
