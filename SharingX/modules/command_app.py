import sys
import traceback
from io import BytesIO, StringIO

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from SharingX import app

async def aexec(code, client, message):

    exec(
        "async def __aexec(client, message):"
        + "\n chat = message.chat.id"
        + "\n r = message.reply_to_message"
        + "\n c = client"
        + "\n m = message"
        + "\n p = print"
        + "".join(
            f"\n {line}"
            for line in code.split("\n")
        )
    )

    return await locals()["__aexec"](
        client,
        message
    )


@app.on_message(
    filters.command("eval")
)
async def _(client, message):

    if len(message.command) < 2:
        return await message.reply(
            "<b>❌ Silahkan kombinasikan dengan kode.</b>"
        )

    cmd = message.text.split(
        " ",
        maxsplit=1
    )[1]

    status_message = await message.reply_text(
        "Processing ..."
    )

    reply_to_ = message

    if message.reply_to_message:
        reply_to_ = message.reply_to_message

    old_stderr = sys.stderr
    old_stdout = sys.stdout

    redirected_output = StringIO()
    redirected_error = StringIO()

    sys.stdout = redirected_output
    sys.stderr = redirected_error

    stdout = None
    stderr = None
    exc = None

    try:

        await aexec(
            cmd,
            client,
            message
        )

    except Exception:

        exc = traceback.format_exc()

    finally:

        stdout = redirected_output.getvalue()
        stderr = redirected_error.getvalue()

        sys.stdout = old_stdout
        sys.stderr = old_stderr

    if exc:
        evaluation = exc

    elif stderr:
        evaluation = stderr

    elif stdout:
        evaluation = stdout

    else:
        evaluation = "Success"

    final_output = (
        f"<b>EVAL</b>:\n"
        f"<pre>{cmd}</pre>\n\n"
        f"<b>OUTPUT</b>:\n"
        f"<pre>{evaluation.strip()}</pre>"
    )

    if len(final_output) > 4096:

        with BytesIO(
            str.encode(final_output)
        ) as out_file:

            out_file.name = "eval.txt"

            await reply_to_.reply_document(
                document=out_file,
                caption=cmd[:1000],
                disable_notification=True,
                quote=True
            )

    else:

        await reply_to_.reply_text(
            final_output,
            quote=True
        )

    try:
        await status_message.delete()
    except Exception:
        pass
        
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
