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

BUTTON_PER_PAGE = 10

@bot.on_message(filters.command("addforcesub"))
async def addforcesub_handler(client, message):
    chat_id = None

    if len(message.command) > 1:
        target = message.command[1]

        if target.startswith("@"):
            try:
                chat = await bot.get_chat(target)
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
                    "❌ Chat ID atau username tidak valid."
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
            "• <code>/addforcesub -100xxxxxxxxxx</code>\n"
            "• <code>/addforcesub @username</code>\n"
            "• Reply ke pesan hasil forward dari channel/grup dengan perintah <code>/addforcesub</code>"
        )

    try:
        await bot.send_message(
            chat_id,
            "✅ Berhasil Disimpan Untuk Forcesub"
        )
    except Exception:
        return await message.reply(
            "❌ Gagal mengirim pesan ke channel/grup.\n"
            "Pastikan bot sudah menjadi admin dan memiliki izin mengirim pesan."
        )

    await add_forcesub(chat_id)

    await message.reply(
        f"✅ Forcesub berhasil ditambahkan.\n\n"
        f"Nama: <b>{(await bot.get_chat(chat_id)).title}</b>\n"
        f"Chat ID: <code>{chat_id}</code>"
    )

async def build_forcesub_menu(page=0):
    forcesubs = await get_forcesubs()

    if not forcesubs:
        return "ℹ️ Belum ada channel forcesub.", None

    start = page * BUTTON_PER_PAGE
    end = start + BUTTON_PER_PAGE

    buttons = []

    for chat_id in forcesubs[start:end]:
        try:
            chat = await bot.get_chat(chat_id)
            name = chat.title
        except Exception:
            name = str(chat_id)

        buttons.append([
            InlineKeyboardButton(
                f"📢 {name}",
                callback_data=f"forcesub_{chat_id}"
            )
        ])

    nav = []

    if page > 0:
        nav.append(
            InlineKeyboardButton(
                "⬅️",
                callback_data=f"forcesub_page_{page-1}"
            )
        )

    if end < len(forcesubs):
        nav.append(
            InlineKeyboardButton(
                "➡️",
                callback_data=f"forcesub_page_{page+1}"
            )
        )

    if nav:
        buttons.append(nav)

    text = (
        "<b>📌 Daftar Forcesub</b>\n\n"
        "Pilih salah satu channel/grup untuk mengelolanya."
    )

    return text, InlineKeyboardMarkup(buttons)

@bot.on_message(filters.command("listforcesub"))
async def listforcesub_handler(client, message):
    text, markup = await build_forcesub_menu()

    await message.reply(
        text,
        reply_markup=markup
    )

@bot.on_callback_query(filters.regex(r"^forcesub_page_(\d+)$"))
async def forcesub_page_callback(client, callback_query):
    page = int(callback_query.matches[0].group(1))

    text, markup = await build_forcesub_menu(page)

    await callback_query.message.edit_text(
        text,
        reply_markup=markup
    )

    await callback_query.answer()

@bot.on_callback_query(filters.regex(r"^forcesub_(-?\d+)$"))
async def forcesub_detail_callback(client, callback_query):
    chat_id = int(callback_query.matches[0].group(1))

    try:
        chat = await bot.get_chat(chat_id)
        title = chat.title
        username = f"@{chat.username}" if chat.username else "-"
    except:
        title = "Tidak diketahui"
        username = "-"

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "🗑 Hapus Forcesub",
                callback_data=f"forcesub_delete_{chat_id}"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Kembali",
                callback_data="forcesub_back"
            )
        ]
    ])

    await callback_query.message.edit_text(
        f"<b>📢 {title}</b>\n\n"
        f"<b>Chat ID:</b>\n<code>{chat_id}</code>\n"
        f"<b>Username:</b> {username}",
        reply_markup=keyboard
    )

    await callback_query.answer()

@bot.on_callback_query(filters.regex(r"^forcesub_delete_(-?\d+)$"))
async def forcesub_delete_callback(client, callback_query):
    chat_id = int(callback_query.matches[0].group(1))

    keyboard = InlineKeyboardMarkup([
        [
            InlineKeyboardButton(
                "✅ Ya, Hapus",
                callback_data=f"forcesub_yes_{chat_id}"
            ),
            InlineKeyboardButton(
                "❌ Batal",
                callback_data=f"forcesub_{chat_id}"
            )
        ]
    ])

    await callback_query.message.edit_text(
        "⚠️ <b>Yakin ingin menghapus channel/grup ini dari Forcesub?</b>",
        reply_markup=keyboard
    )

    await callback_query.answer()

@bot.on_callback_query(filters.regex(r"^forcesub_yes_(-?\d+)$"))
async def forcesub_yes_callback(client, callback_query):
    chat_id = int(callback_query.matches[0].group(1))

    await del_forcesub(chat_id)

    text, markup = await build_forcesub_menu()

    await callback_query.message.edit_text(
        "✅ Berhasil dihapus dari Forcesub.\n\n" + text,
        reply_markup=markup
    )

    await callback_query.answer("Berhasil dihapus")


@bot.on_callback_query(filters.regex("^forcesub_back$"))
async def forcesub_back_callback(client, callback_query):
    text, markup = await build_forcesub_menu()

    await callback_query.message.edit_text(
        text,
        reply_markup=markup
    )

    await callback_query.answer()
    
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
