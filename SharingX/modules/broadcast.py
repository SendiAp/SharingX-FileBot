import time
import asyncio

from pyrogram.errors import (
    FloodWait,
    UserIsBlocked,
    InputUserDeactivated
)

async def remove_duplicates(users):
    seen = set()
    unique_users = []
    
    for user in users:
        if user not in seen:
            seen.add(user)
            unique_users.append(user)
        else:
            await del_user(user)
    return unique_users
  
@bot.on_message(filters.command(["broadcast", "gcast"]) & filters.private & filters.user(OWNER_ID))
async def broadcast(client, message):

    if not message.reply_to_message:
        return await message.reply(
            "❌ Reply Pesan Apapun!",
            quote=True
        )

    users = await get_user()

    if not users:
        return await message.reply(
            "⚠️ Tidak Ada Pengguna Yang Terdaftar!",
            quote=True
        )

    users = await remove_duplicates(users)

    broadcast_msg = message.reply_to_message

    total = len(users)
    successful = 0
    blocked = 0
    deleted = 0
    unsuccessful = 0

    start_time = time.time()

    pls_wait = await message.reply(
        "📡 Broadcast Sedang Berlangsung...",
        quote=True
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
            await del_user(user_id)
            blocked += 1

        except InputUserDeactivated:
            await del_user(user_id)
            deleted += 1

        except Exception:
            await del_user(user_id)
            unsuccessful += 1

    elapsed = int(time.time() - start_time)

    hours, rem = divmod(elapsed, 3600)
    minutes, seconds = divmod(rem, 60)

    process_time = f"{hours:02}:{minutes:02}:{seconds:02}"

    status = (
        "<b>✅ Broadcast Selesai</b>\n\n"
        f"👥 Total User : <code>{total}</code>\n"
        f"📨 Berhasil : <code>{successful}</code>\n"
        f"❌ Gagal : <code>{unsuccessful}</code>\n"
        f"🚫 Diblokir : <code>{blocked}</code>\n"
        f"🗑 Akun Terhapus : <code>{deleted}</code>\n"
        f"⏱ Waktu Proses : <code>{process_time}</code>"
    )

    await pls_wait.edit(status)
