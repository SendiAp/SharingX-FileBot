import sys, os
import asyncio
import traceback
import importlib
from io import BytesIO, StringIO

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from SharingX import app, Bot
from SharingX.helper.database import add_bot
from SharingX.modules import loadModule

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):

    await message.reply_text(
        "<b>🤖 Welcome To SharingX Bot Manager</b>\n\n"
        "Silahkan pilih menu di bawah untuk membuat bot baru.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ Create Bot",
                        callback_data="create_bot"
                    )
                ]
            ]
        )
    )
  
@app.on_callback_query(filters.regex("create_bot"))
async def create_bot(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    callback = await callback_query.edit_message_text(
        "<b>🤖 Masukkan API ID Anda:</b>\n\n"
        "__Dapatkan di web [my.telegram.org](https://my.telegram.org)__"
    )

    while True:
        user_msg = await app.listen(user_id)

        try:
            api_id = int(user_msg.text)
            await user_msg.delete()
            break

        except ValueError:
            await user_msg.delete()

            warn = await client.send_message(
                user_id,
                "<b>⚠️ API ID harus berupa angka!</b>"
            )

            await asyncio.sleep(2)
            await warn.delete()

    await callback.edit(
        "<b>🤖 Masukkan API HASH Anda:</b>\n\n"
        "__Dapatkan di web [my.telegram.org](https://my.telegram.org)__"
    )

    user_msg = await app.listen(user_id)

    api_hash = user_msg.text.strip()

    await user_msg.delete()

    await callback.edit(
        "<b>🤖 Masukkan BOT TOKEN Anda:</b>\n\n"
        "__Dapatkan di BOT @BotFather__"
    )

    user_msg = await app.listen(user_id)

    bot_token = user_msg.text.strip()

    await user_msg.delete()

    await callback.edit(
        "<b>🗄 Masukkan MongoDB URL:</b>\n\n"
        "Contoh:\n"
        "<code>mongodb+srv://user:pass@cluster.mongodb.net/</code>"
    )

    user_msg = await app.listen(user_id)

    mongo_url = user_msg.text.strip()

    await user_msg.delete()

    await callback.edit(
        "<b>📂 Masukkan Nama Database:</b>\n\n"
        "Default: <code>sharingx</code>"
    )

    user_msg = await app.listen(user_id)

    database = user_msg.text.strip()

    await user_msg.delete()

    if not database:
        database = "sharingx"

    await callback.edit(
        "<b>⏳ Mengecek data bot...</b>"
    )

    bot_id = bot_token.split(":")[0]

    media = Bot(
        name=str(bot_id),
        api_id=api_id,
        api_hash=api_hash,
        bot_token=bot_token
    )

    try:
        media.in_memory = False

        await media.start()

        me = await media.get_me()

        await callback.edit(
            f"<b>✅ Bot berhasil ditemukan!</b>\n\n"
            f"<b>• Nama:</b> {me.first_name}\n"
            f"<b>• Username:</b> @{me.username}\n\n"
            f"<b>⏳ Menyimpan konfigurasi...</b>"
        )

    except Exception as e:

        error = str(e)

        if "ACCESS_TOKEN_INVALID" in error:
            return await callback.edit(
                "<b>⚠️ BOT TOKEN TIDAK VALID</b>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "➕ Mulai Lagi",
                                callback_data="create_bot"
                            )
                        ]
                    ]
                )
            )


        if "API_ID_INVALID" in error:
            return await callback.edit(
                "<b>⚠️ API ID / API HASH TIDAK VALID</b>",
                reply_markup=InlineKeyboardMarkup(
                    [
                        [
                            InlineKeyboardButton(
                                "➕ Mulai Lagi",
                                callback_data="create_bot"
                            )
                        ]
                    ]
                )
            )


        return await callback.edit(
            f"<b>❌ ERROR:</b>\n<code>{error}</code>"
        )

    await add_bot(
        str(media.me.id),
        api_id,
        api_hash,
        bot_token,
        mongo_url,
        database
    )

    await asyncio.sleep(2)

    await callback.edit(
        "<b>✅ Bot Anda Berhasil Diaktifkan!</b>\n\n"
        f"<b>• Username:</b> @{me.username}\n"
        f"<b>• Database:</b> <code>{database}</code>",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        f"@{me.username}",
                        url=f"https://t.me/{me.username}"
                    )
                ]
            ]
        )
    )

    for mod in loadModule():
        importlib.reload(
            importlib.import_module(
                f"SharingX.modules.{mod}"
            )
        )


    try:
        os.popen(f"rm {bot_id}*")
    except:
        pass

async def aexec(code, client, message):
    exec(
        "async def __aexec(client, message): "
        + "\n chat = message.chat.id"
        + "\n r = message.reply_to_message"
        + "\n c = client"
        + "\n m = message"
        + "\n p = print"
        + "".join(f"\n {l_}" for l_ in code.split("\n"))
    )
    return await locals()["__aexec"](client, message)

@app.on_message(filters.command("e"))
async def _(client, message):
    cmd = message.text.split(" ", maxsplit=1)[1]
    if len(message.command) < 2:
        return await message.reply("Silahkan kombinasikan dengan kode")
    status_message = await message.reply_text("Processing ...")
    reply_to_ = message
    if message.reply_to_message:
        reply_to_ = message.reply_to_message

    old_stderr = sys.stderr
    old_stdout = sys.stdout
    redirected_output = sys.stdout = StringIO()
    redirected_error = sys.stderr = StringIO()
    stdout, stderr, exc = None, None, None

    try:
        await aexec(cmd, client, message)
    except Exception:
        exc = traceback.format_exc()

    stdout = redirected_output.getvalue()
    stderr = redirected_error.getvalue()
    sys.stdout = old_stdout
    sys.stderr = old_stderr

    evaluation = ""
    if exc:
        evaluation = exc
    elif stderr:
        evaluation = stderr
    elif stdout:
        evaluation = stdout
    else:
        evaluation = "Success"

    final_output = f"""
<b>EVAL</b>:
```
{cmd}
```
<b>OUTPUT</b>:
```
{evaluation.strip()}
```
"""

    if len(final_output) > 4096:
        with BytesIO(str.encode(final_output)) as out_file:
            out_file.name = "eval.text"
            await reply_to_.reply_document(
                document=out_file,
                caption=cmd[: 4096 // 4 - 1],
                disable_notification=True,
                quote=True,
            )
    else:
        await reply_to_.reply_text(final_output, quote=True)
    await status_message.delete()
