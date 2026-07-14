import asyncio

from SharingX import bot
from SharingX.helper.database import (
    add_forcesub,
    del_forcesub,
    get_forcesub,
    get_force_sub_count,
    get_force_sub_status,
    is_forcesub,
    set_force_sub_status,
)

from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)
from pyrogram.errors import (
    UserNotParticipant,
    ChatAdminRequired,
    ChatWriteForbidden,
    PeerIdInvalid
)

MAX_FORCESUB = 50

def force_channel(channels, username):
    buttons = []

    for i, chat in enumerate(channels, start=1):
        if str(chat).startswith("-100"):
            url = f"https://t.me/c/{str(chat)[4:]}"
        else:
            url = f"https://t.me/{chat}"

        buttons.append(
            [
                InlineKeyboardButton(
                    f"📢 Join {i}",
                    url=url
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                "🔄 Coba Lagi",
                url=f"https://t.me/{username}?start=start"
            )
        ]
    )

    return InlineKeyboardMarkup(buttons)

@bot.on_message(filters.command("forcesub") & filters.private)
async def forcesub_cmd(client, message):

    if len(message.command) == 1:
        return await message.reply_text(
            "<b>ForceSub Manager</b>\n\n"
            "<code>/forcesub add -100xxxxxxxxxx</code>\n"
            "<code>/forcesub del -100xxxxxxxxxx</code>\n"
            "<code>/forcesub list</code>\n"
            "<code>/forcesub on</code>\n"
            "<code>/forcesub off</code>"
        )

    action = message.command[1].lower()

    if action == "add":

        if len(message.command) != 3:
            return await message.reply_text(
                "<code>/forcesub add -100xxxxxxxxxx</code>"
            )

        chat = message.command[2]

        if await get_force_sub_count() >= MAX_FORCESUB:
            return await message.reply_text(
                f"❌ Maksimal {MAX_FORCESUB} ForceSub."
            )

        if await is_forcesub(chat):
            return await message.reply_text(
                "❌ Channel/Grup sudah terdaftar."
            )

        try:
            info = await bot.get_chat(chat)

            await add_forcesub(chat)

            try:
                await bot.send_message(
                    info.id,
                    "✅ Bot berhasil dijadikan ForceSub."
                )
            except ChatWriteForbidden:
                pass

            return await message.reply_text(
                f"✅ Berhasil ditambahkan.\n\n"
                f"**{info.title}**\n"
                f"`{chat}`"
            )

        except Exception as e:
            return await message.reply_text(
                f"❌ {e}"
            )

    elif action == "del":

        if len(message.command) != 3:
            return await message.reply_text(
                "<code>/forcesub del -100xxxxxxxxxx</code>"
            )

        chat = message.command[2]

        if not await is_forcesub(chat):
            return await message.reply_text(
                "❌ Data tidak ditemukan."
            )

        await del_forcesub(chat)

        return await message.reply_text(
            "✅ ForceSub berhasil dihapus."
        )

    elif action == "list":

        data = await get_forcesub()

        if not data:
            return await message.reply_text(
                "❌ Belum ada ForceSub."
            )

        text = "<b>Daftar ForceSub</b>\n\n"

        for no, chat in enumerate(data, start=1):
            try:
                info = await bot.get_chat(chat)
                text += (
                    f"{no}. {info.title}\n"
                    f"<code>{chat}</code>\n\n"
                )
            except Exception:
                text += (
                    f"{no}. <code>{chat}</code>\n\n"
                )

        return await message.reply_text(text)

    elif action == "on":

        await set_force_sub_status(True)

        return await message.reply_text(
            "✅ ForceSub berhasil diaktifkan."
        )

    elif action == "off":

        await set_force_sub_status(False)

        return await message.reply_text(
            "✅ ForceSub berhasil dinonaktifkan."
        )

    else:
        return await message.reply_text(
            "❌ Command tidak dikenal."
        )

@bot.on_message(filters.private & filters.incoming, group=-1)
async def check_forcesub(client, message):

    if message.from_user is None:
        return

    if message.from_user.is_bot:
        return

    if message.text and message.text.startswith("/forcesub"):
        return

    status = await get_force_sub_status()

    if not status:
        return

    channels = await get_forcesub()

    if not channels:
        return

    not_join = []

    for chat in channels:

        try:
            member = await bot.get_chat_member(chat, message.from_user.id)

            if member.status in (
                "left",
                "kicked",
                "restricted"
            ):
                not_join.append(chat)

        except UserNotParticipant:
            not_join.append(chat)

        except ChatAdminRequired:
            return await message.reply_text(
                f"❌ Bot bukan admin di\n<code>{chat}</code>"
            )

        except PeerIdInvalid:
            continue

        except Exception:
            continue

    if not not_join:
        return

    buttons = []

    for i, chat in enumerate(not_join, start=1):

        try:
            info = await bot.get_chat(chat)

            if info.username:
                url = f"https://t.me/{info.username}"
            else:
                url = info.invite_link

            buttons.append(
                [
                    InlineKeyboardButton(
                        f"📢 Join {i}",
                        url=url
                    )
                ]
            )

        except Exception:
            continue

    buttons.append(
        [
            InlineKeyboardButton(
                "🔄 Coba Lagi",
                url=f"https://t.me/{(await bot.get_me()).username}?start=start"
            )
        ]
    )

    await message.reply_text(
        f"<b>👋 Halo {message.from_user.mention}</b>\n\n"
        "Anda harus bergabung ke seluruh channel/grup berikut terlebih dahulu sebelum menggunakan bot.",
        reply_markup=InlineKeyboardMarkup(buttons),
        disable_web_page_preview=True
    )

    await message.stop_propagation()
