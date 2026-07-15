import asyncio

from SharingX import bot
from SharingX.helper.database import (
    add_forcesub,
    del_forcesub,
    get_forcesubs
)

from pyrogram import filters
from pyrogram.errors import (
    ChatAdminRequired,
    UserNotParticipant,
    ChatWriteForbidden
)

from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    ReplyKeyboardMarkup
)

@bot.on_message(filters.command("addforcesub"))
async def addforcesub_handler(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "❌ Gunakan format:\n<code>/addforcesub -100xxxxxxxxxx</code>"
        )

    try:
        chat_id = int(message.command[1])
    except ValueError:
        return await message.reply("❌ Chat ID harus berupa angka!")

    await add_forcesub(chat_id)

    await message.reply(
        f"✅ Channel forcesub berhasil ditambahkan.\n\n"
        f"Chat ID: <code>{chat_id}</code>"
    )

@bot.on_message(filters.command("delforcesub"))
async def delforcesub_handler(client, message):
    if len(message.command) < 2:
        return await message.reply(
            "❌ Gunakan format:\n<code>/delforcesub -100xxxxxxxxxx</code>"
        )

    try:
        chat_id = int(message.command[1])
    except ValueError:
        return await message.reply("❌ Chat ID harus berupa angka!")

    await del_forcesub(chat_id)

    await message.reply(
        f"🗑 Channel forcesub berhasil dihapus.\n\n"
        f"Chat ID: <code>{chat_id}</code>"
    )

@bot.on_message(filters.command("listforcesub"))
async def listforcesub_handler(client, message):
    forcesubs = await get_forcesubs()

    if not forcesubs:
        return await message.reply("ℹ️ Belum ada channel forcesub.")

    text = "<b>📌 Daftar Channel Forcesub</b>\n\n"

    for no, chat_id in enumerate(forcesubs, 1):
        try:
            chat = await bot.get_chat(chat_id)
            text += f"{no}. {chat.title}\n<code>{chat_id}</code>\n\n"
        except Exception:
            text += f"{no}. <code>{chat_id}</code> (Tidak dapat diakses)\n\n"

    await message.reply(text)


@bot.on_message(filters.private & filters.incoming, group=-1)
async def forcesub(client, message):
    if not message.from_user:
        return

    forcesubs = await get_forcesubs()

    if not forcesubs:
        return

    not_joined = []

    for chat_id in forcesubs:
        try:
            await bot.get_chat_member(chat_id, message.from_user.id)
        except UserNotParticipant:
            not_joined.append(chat_id)
        except Exception:
            continue

    if not not_joined:
        return

    keyboard = []
    row = []

    for chat_id in not_joined:
        try:
            chat = await bot.get_chat(chat_id)

            if chat.username:
                url = f"https://t.me/{chat.username}"
            else:
                invite = chat.invite_link

                if not invite:
                    try:
                        invite = await bot.create_chat_invite_link(chat_id)
                        invite = invite.invite_link
                    except Exception:
                        continue

                url = invite

            row.append(
                InlineKeyboardButton(
                    chat.title,
                    url=url
                )
            )

            if len(row) == 2:
                keyboard.append(row)
                row = []

        except Exception:
            continue

    if row:
        keyboard.append(row)

    me = await bot.get_me()

    keyboard.append(
        [
            InlineKeyboardButton(
                "✅ Coba Lagi",
                url=f"https://t.me/{me.username}?start=start"
            )
        ]
    )

    await message.reply(
        f"👋 Hai {message.from_user.mention},\n\n"
        "Untuk menggunakan bot ini, silakan bergabung ke seluruh channel di bawah terlebih dahulu.",
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )

    await message.stop_propagation()
