import asyncio

from pyrogram import filters
from pyrogram.errors import (
    UserNotParticipant,
)

from pyrogram.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
)

from SharingX import Bot
from SharingX.modules.db import (
    add_forcesub,
    del_forcesub,
    get_forcesubs,
    get_forcesub_button_mode,
    set_forcesub_button_mode,
)

BUTTON_PER_PAGE = 10

@Bot.on_message(filters.command("addfc"))
async def addforcesub_handler(client, message):

    chat_id = None

    if len(message.command) > 1:

        target = message.command[1]

        if target.startswith("@"):

            try:
                chat = await client.get_chat(target)
                chat_id = chat.id

            except Exception:
                return await message.reply_text(
                    "<b>❌ Username Channel/Groups Tidak Ditemukan!</b>"
                )

        else:

            try:
                chat_id = int(target)

            except ValueError:
                return await message.reply_text(
                    "<b>❌ ChatID Atau Username Tidak Valid!</b>"
                )

    elif message.reply_to_message:

        reply = message.reply_to_message

        if reply.forward_from_chat:
            chat_id = reply.forward_from_chat.id

        elif reply.sender_chat:
            chat_id = reply.sender_chat.id

        else:
            return await message.reply_text(
                "<b>❌ Reply Pesan Dari Hasil Forward!</b>"
            )

    else:
        
        return await message.reply_text(
            "<b>Gunakan Salah Satu Cara Berikut:</b>\n\n"
            "• <code>/addfc -100xxxxxxxxxx</code>\n"
            "• <code>/addfc @username</code>\n"
            "• Reply Pesan Dari Hasil Forward Channel/Groups <code>/addfc</code>"
        )

    try:
        await client.send_message(chat_id, "✅ Berhasil disimpan sebagai Force Subscribe.")
    except Exception:
        return await message.reply_text(
            "<b>❌ Bot tidak dapat mengirim pesan ke channel/grup.</b>\n\n"
            "Pastikan bot sudah menjadi admin dan memiliki izin mengirim pesan."
        )

    await add_forcesub(client, chat_id)

    chat = await client.get_chat(chat_id)

    await message.reply_text(
        f"<b>✅ Forcesub Berhasil Ditambahkan Dari Database!</b>\n\n"
        f"<b>📢 Nama :</b> {chat.title}\n"
        f"<b>🆔 ChatID :</b> `{chat_id}\n\n"
        f"/listfc - Untuk Mengelola Forcesub Anda!"
    )

async def build_forcesub_menu(client, page=0):

    forcesubs = await get_forcesubs(client)

    if not forcesubs:
        return ("<b>ℹ️ Belum Ada Forcesub Yang Tersimpan Didatabase.</b>", None)

    start = page * BUTTON_PER_PAGE
    end = start + BUTTON_PER_PAGE

    buttons = []

    for chat_id in forcesubs[start:end]:

        try:
            chat = await client.get_chat(chat_id)
            title = chat.title

        except Exception:
            title = str(chat_id)

        buttons.append(
            [
                InlineKeyboardButton(
                    f"{title}",
                    callback_data=f"forcesub_{chat_id}"
                )
            ]
        )

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

    return (
        "<b>👨‍💻 MANAGE FORCESUB</b>\n\n"
        "__Pilih Salah Satu Forcesub Yang Ingin Anda Kelola, Atau Lihat Detailnya.__\n\n"
        "<b>⚠️ Hubungi Developer Jika Ada Sesuatu Yang Error.</b>",
        InlineKeyboardMarkup(buttons)
    )

@Bot.on_message(filters.command("listfc"))
async def listforcesub_handler(client, message):
    try:
        text, markup = await build_forcesub_menu(client)
        await message.reply_text(text, reply_markup=markup)
    except Exception as e:
        return await message.reply_text(f"<b>Terjadi Kesalahan:</b> `{str(e)}`")
        
@Bot.on_callback_query(filters.regex(r"^forcesub_page_(\d+)$"))
async def forcesub_page_callback(client, callback_query):
    try:
        page = int(callback_query.matches[0].group(1))
        text, markup = await build_forcesub_menu(client, page)
        await callback_query.message.edit_text(text, reply_markup=markup)
        await callback_query.answer()
    except Exception as e:
        return await callback_query.message.edit_text(f"<b>Terjadi Kesalahan:</b> `{str(e)}`")

@Bot.on_callback_query(filters.regex(r"^forcesub_(-?\d+)$"))
async def forcesub_detail_callback(client, callback_query):

    chat_id = int(callback_query.matches[0].group(1))

    try:
        chat = await client.get_chat(chat_id)
        title = chat.title
        username = (f"@{chat.username}" if chat.username else "-")
    except Exception:
        title = "Unknown"
        username = "-"

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "🗑 Delete",
                    callback_data=f"forcesub_delete_{chat_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Kembali",
                    callback_data="forcesub_back"
                )
            ]
        ]
    )

    await callback_query.message.edit_text(
        f"<b>🔐 INFORMASI DATA</b>\n\n"
        f"<b>📢 Nama: {title}</b>\n"
        f"<b>🔗 Username:</b> {username}\n"
        f"<b>🆔 ChatID: {chat_id}\n",
        reply_markup=keyboard
    )

    await callback_query.answer()

@Bot.on_callback_query(filters.regex(r"^forcesub_delete_(-?\d+)$"))
async def forcesub_delete_callback(client, callback_query):

    chat_id = int(
        callback_query.matches[0].group(1)
    )

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "✅ Ya",
                    callback_data=f"forcesub_yes_{chat_id}"
                ),
                InlineKeyboardButton(
                    "❌ Tidak",
                    callback_data=f"forcesub_{chat_id}"
                )
            ]
        ]
    )

    await callback_query.message.edit_text(
        "<b>⚠️ Apa Kamu Yakin Ingin Menghapus Forcesub Ini Dari Database?</b>",
        reply_markup=keyboard
    )

    await callback_query.answer()

@Bot.on_callback_query(filters.regex(r"^forcesub_yes_(-?\d+)$"))
async def forcesub_yes_callback(client, callback_query):
    try:
        chat_id = int(callback_query.matches[0].group(1))
        await del_forcesub(client, chat_id)
        text, markup = await build_forcesub_menu(client)
        await callback_query.message.edit_text("✅ Berhasil Dihapus Dari Database!\n\n" + text, reply_markup=markup)
    except Exception as e:
        return await callback_query.message.edit_text(f"<b>Terjadi Kesalahan:</b> `{str(e)}`")

@Bot.on_message(filters.command("modefc"))
async def forcesub_button(client, message):

    mode = await get_forcesub_button_mode(client)

    mode_text = {
        "text": "Text",
        "username": "Username",
        "name": "Nama"
    }.get(mode, "Text")

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📝 Text",
                    callback_data="fsbtn_text"
                )
            ],
            [
                InlineKeyboardButton(
                    "👤 Username",
                    callback_data="fsbtn_username"
                )
            ],
            [
                InlineKeyboardButton(
                    "📢 Nama",
                    callback_data="fsbtn_name"
                )
            ]
        ]
    )

    await message.reply_text(
        "<b>⚙️ Force Subscribe Button</b>\n\n"
        f"<b>Mode Saat Ini:</b> <code>{mode_text}</code>\n\n"
        "Silakan pilih mode tombol yang akan digunakan.",
        reply_markup=keyboard
    )

@Bot.on_callback_query(filters.regex(r"^fsbtn_(text|username|name)$"))
async def forcesub_button_callback(client, callback_query):

    mode = callback_query.matches[0].group(1)

    await set_forcesub_button_mode(client, mode)

    mode_text = {
        "text": "Text",
        "username": "Username",
        "name": "Nama"
    }[mode]

    keyboard = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton(
                    "📝 Text",
                    callback_data="fsbtn_text"
                )
            ],
            [
                InlineKeyboardButton(
                    "👤 Username",
                    callback_data="fsbtn_username"
                )
            ],
            [
                InlineKeyboardButton(
                    "📢 Nama",
                    callback_data="fsbtn_name"
                )
            ]
        ]
    )

    await callback_query.edit_message_text(
        "<b>⚙️ Force Subscribe Button</b>\n\n"
        f"<b>Mode Saat Ini:</b> <code>{mode_text}</code>\n\n"
        "Silakan pilih mode tombol yang akan digunakan.",
        reply_markup=keyboard
    )

    await callback_query.answer(f"✅ Mode Berhasil Diubah Menjadi {mode_text}", show_alert=True)
    
@Bot.on_callback_query(filters.regex("^forcesub_back$"))
async def forcesub_back_callback(client, callback_query):
    try:
        text, markup = await build_forcesub_menu(client)
        await callback_query.message.edit_text(text, reply_markup=markup)
        await callback_query.answer()
    except Exception as e:
        return await callback_query.message.edit_text(f"<b>Terjadi Kesalahan:</b> `{str(e)}`")

@Bot.on_message(filters.private & filters.incoming, group=-1)
async def forcesub(client, message):

    if not message.from_user:
        return

    forcesubs = await get_forcesubs(client)

    if not forcesubs:
        return

    mode = await get_forcesub_button_mode(client)

    not_joined = []

    for chat_id in forcesubs:
        try:
            await client.get_chat_member(
                chat_id,
                message.from_user.id
            )

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
            chat = await client.get_chat(chat_id)

            if chat.username:
                url = f"https://t.me/{chat.username}"
            else:
                invite = chat.invite_link

                if not invite:
                    try:
                        invite = await client.create_chat_invite_link(chat_id)
                        invite = invite.invite_link
                    except Exception:
                        continue

                url = invite

            if mode == "text":
                text = (
                    "Join Channel"
                    if chat.type.name.lower() == "channel"
                    else "Join Groups"
                )

            elif mode == "username":
                text = (
                    f"@{chat.username}"
                    if chat.username
                    else "🔗 Join"
                )

            else:
                text = chat.title

            row.append(
                InlineKeyboardButton(
                    text,
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

    me = await client.get_me()

    keyboard.append(
        [
            InlineKeyboardButton(
                "✅ Coba Lagi",
                url=f"https://t.me/{me.username}?start=start"
            )
        ]
    )

    await message.reply_text(
        f"👋 Hai {message.from_user.mention},\n\n"
        f"__Anda Harus Bergabung Di Channel/Group Saya Terlebih Dahulu Untuk Menggunakan Bot Ini.__\n\n"
        f"Silahkan Bergabung Channel/Groups:",
        reply_markup=InlineKeyboardMarkup(keyboard),
        disable_web_page_preview=True
    )

    await message.stop_propagation()
