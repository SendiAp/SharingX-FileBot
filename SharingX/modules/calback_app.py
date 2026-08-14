from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from SharingX import app

@app.on_callback_query(filters.regex(r"^command$"))
async def command(client, callback_query):
    text = (
        "<b>Last Updated: August 11, 2026</b>\n\n"

        "__Beberapa Command Yang Diterapkan Dibot Ini Para Penyewa.__\n\n"
        
        "<b><u>1. Link Sharing: [OWNER & ADMIN]</b>\n\n"
        "<b>Function:</b> __Jika Mematikan Link Tidak Terbuat Otomatis, Saat Dalam Mengatur Bot Anda.__\n\n"
        "<pre>• `/link on` | <b>Mengaktifkan</b></pre>\n"
        "<pre>• `/link off` | <b>Menonaktifkan</b></pre>\n\n"

        "<b><u>2. Logger Database: [OWNER & ADMIN]</b>\n\n"
        "<b>Function:</b> __Menyimpan Logger Database, Ini Penting Sekali.__\n\n"
        "<pre>• `/adddb` | <b>ID - Username - Reply</b></pre>\n"
        "<pre>• `/deldb` | <b>ID - Username - Reply</b></pre>\n\n"

        "<b><u>3. Protect File: [OWNER & ADMIN]</b>\n\n"
        "<b>Function:</b> __Jika Diaktifkan File/Media Yang Anda Buat Tidak Bisa Disimpan, Teruskan, Atau Di Screenshot.__\n\n"
        "<pre>• `/protect true` | <b>Mengaktifkan</b></pre>\n"
        "<pre>• `/protect false` | <b>Menonaktifkan</b></pre>\n\n"

        "<b><u>4. Forcesub Button: [OWNER & ADMIN]</b>\n\n"
        "<b>Function:</b> __Untuk Memaksa Pengguna Memasuki Channel/Groups Anda.__\n\n"
        "<pre>• `/addfc` | <b>ID - Username - Reply</b></pre>\n"
        "<pre>• `/delfc` | <b>ID - Username - Reply</b></pre>\n\n"
        
        "<b><u>5. Admin: [OWNER]</b>\n\n"
        "<b>Function:</b> __Menambahkan Admin Untuk Menggunakan Beberapa Fitur.__\n\n"
        "<pre>• `/addadmin` | <b>ID - Username - Reply</b></pre>\n"
        "<pre>• `/deladmin` | <b>ID - Username - Reply</b></pre>\n"
        "<pre>• `/listadmin` | <b>Daftar Admin</b></pre>\n\n"

        "<b><u>6. Broadcast: [OWNER]</b>\n\n"
        "<b>Function:</b> __Mengirimkan Siaran, Seperti Text All Media, Bahakan Tombol.__\n\n"
        "<pre>• `/broadcast` | <b>Reply Pesan</b></pre>\n\n"

        "<b>© SharingX</b>"
    )

    await callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔙 Kembali",
                    callback_data="back_bot_start"
                )
            ]
        ])
    )
