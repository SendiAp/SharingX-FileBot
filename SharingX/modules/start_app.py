import sys, os
import asyncio
import traceback
import importlib
from pymongo import MongoClient
from io import BytesIO, StringIO

from pyrogram import filters
from pyrogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton

from SharingX import app, Bot
from SharingX.helper.database import (
    add_bot,
    get_bot_data,
    get_user_bots,
    add_user_bot,
    remove_user_bot,
    remove_bot,
    set_bot_status,
)
from SharingX.modules import loadModule

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):

    await message.reply_text(
        "<b>🤖 Welcome To SharingX Bot Manager</b>\n\n"
        "Silahkan pilih menu di bawah.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ Create Bot",
                        callback_data="create_bot"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📦 My Bots",
                        callback_data="my_bots"
                    )
                ]
            ]
        )
    )

@app.on_callback_query(filters.regex("^back_start$"))
async def back_start(client, callback_query: CallbackQuery):

    await callback_query.edit_message_text(
        "<b>🤖 Welcome To SharingX Bot Manager</b>\n\n"
        "Silahkan pilih menu di bawah.",
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "➕ Create Bot",
                        callback_data="create_bot"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "📦 My Bots",
                        callback_data="my_bots"
                    )
                ]
            ]
        )
    )

@app.on_callback_query(filters.regex("^my_bots$"))
async def my_bots(client, callback_query: CallbackQuery):
    user_id = callback_query.from_user.id

    bots = await get_user_bots(user_id)

    if not bots:
        return await callback_query.edit_message_text(
            "<b>📦 My Bots</b>\n\n"
            "Anda belum memiliki bot.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "➕ Create Bot",
                            callback_data="create_bot"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "⬅️ Back",
                            callback_data="back_start"
                        )
                    ]
                ]
            )
        )

    buttons = []

    for bot in bots:

        status = bot.get("status", "running")
        if status == "running":
            emoji = "🟢"
        elif status == "restart":
            emoji = "🔄"
        else:
            emoji = "🔴"

        bot_id = bot['bot_id']
        bot = Bot.get_instance(bot_id)
        if bot:
            me = await bot.get_me()
            username = me.username
            first_name = me.first_name
            text = f"@{username}"
        
        buttons.append(
            [
                InlineKeyboardButton(
                    text,
                    callback_data=f"bot_{bot_id}"
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="back_start"
            )
        ]
    )

    await callback_query.edit_message_text(
        f"<b>📦 My Bots ({len(bots)})</b>\n\n"
        "Silahkan pilih bot yang ingin dikelola.",
        reply_markup=InlineKeyboardMarkup(buttons)
    )

@app.on_callback_query(filters.regex(r"^bot_(.+)$"))
async def bot_settings(client, callback_query: CallbackQuery):

    bot_id = callback_query.data.split("_", 1)[1]

    bot = await get_bot_data(bot_id)

    if not bot:
        return await callback_query.answer(
            "Bot tidak ditemukan.",
            show_alert=True
        )

    status = bot.get("status", "running")
    
    if status == "running":
        status_text = "🟢 Running"
    elif status == "stopped":
        status_text = "🔴 Stopped"
    elif status == "restart":
        status_text = "🔄 Restarting"
    else:
        status_text = "🤖 Crash"

    username = None
    first_name = "⚠️ Bot Sedang Dalam Penghentian"
    robot = Bot.get_instance(bot['bot_id'])
    if robot:
        me = await robot.get_me()
        username = me.username
        first_name = me.first_name
        
    text = (
        "<b>⚙️ Setting Bots</b>\n\n"
        f"<b>🤖 Nama :</b> [{first_name}](t.me/{username})\n"
        f"<b>🆔 Bot:</b> <code>{bot['bot_id']}</code>\n"
        f"<b>👨‍💻 Status :</b> {status_text}\n"
        f"<b>📂 Database :</b> <code>{bot.get('database', 'sharingx')}</code>"
    )

    await callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(
            [
                [
                    InlineKeyboardButton(
                        "▶️ Start",
                        callback_data=f"startbot_{bot_id}"
                    ),
                    InlineKeyboardButton(
                        "⏸ Stop",
                        callback_data=f"stopbot_{bot_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔄 Restart",
                        callback_data=f"restartbot_{bot_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🗑 Delete",
                        callback_data=f"deletebot_{bot_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "⬅️ Back",
                        callback_data="my_bots"
                    )
                ]
            ]
        )
    )

@app.on_callback_query(filters.regex(r"^stopbot_(.+)$"))
async def stop_bot(client, callback_query: CallbackQuery):

    bot_id = callback_query.data.split("_", 1)[1]

    data = await get_bot_data(bot_id)

    if not data:
        return await callback_query.answer(
            "Bot tidak ditemukan.",
            show_alert=True
        )

    bot = Bot.get_instance(bot_id)

    if bot is None:
        await set_bot_status(bot_id, "stopped")

        return await callback_query.answer(
            "Bot sudah berhenti.",
            show_alert=True
        )

    try:
        await bot.stop()

        await set_bot_status(bot_id, "stopped")

        await callback_query.answer(
            "Bot berhasil dihentikan.",
            show_alert=True
        )
        
    except Exception as e:
        return await callback_query.answer(
            str(e),
            show_alert=True
        )
        
    await bot_settings(client, callback_query)
    
@app.on_callback_query(filters.regex(r"^startbot_(.+)$"))
async def start_bot(client, callback_query: CallbackQuery):

    bot_id = callback_query.data.split("_", 1)[1]

    data = await get_bot_data(bot_id)

    if not data:
        return await callback_query.answer(
            "Bot tidak ditemukan.",
            show_alert=True
        )

    if Bot.get_instance(bot_id):
        return await callback_query.answer(
            "Bot sudah berjalan.",
            show_alert=True
        )

    try:
        media = Bot(
            name=str(data["bot_id"]),
            api_id=data["api_id"],
            api_hash=data["api_hash"],
            bot_token=data["bot_token"]
        )

        mongo = MongoClient(data["mongo_url"])

        media.mongo = mongo
        media.db = mongo[data.get("database", "sharingx")]

        await media.start()

        for mod in loadModule():
            importlib.reload(
                importlib.import_module(
                    f"SharingX.modules.{mod}"
                )
            )
            
        await set_bot_status(bot_id, "running")

        await callback_query.answer(
            "Bot berhasil dijalankan.",
            show_alert=True
        )

    except Exception as e:
        return await callback_query.answer(
            str(e),
            show_alert=True
        )

    await bot_settings(client, callback_query)

@app.on_callback_query(filters.regex(r"^restartbot_(.+)$"))
async def restart_bot(client, callback_query: CallbackQuery):

    bot_id = callback_query.data.split("_", 1)[1]

    data = await get_bot_data(bot_id)

    if not data:
        return await callback_query.answer(
            "Bot tidak ditemukan.",
            show_alert=True
        )

    old_bot = Bot.get_instance(bot_id)

    if old_bot is None:
        return await callback_query.answer(
            "Bot sedang tidak berjalan.",
            show_alert=True
        )

    try:
        await set_bot_status(bot_id, "restart")

        await callback_query.answer(
            "✅ Bot berhasil direstart.",
            show_alert=True
        )

        await bot_settings(client, callback_query)
        
        await old_bot.stop()

        await asyncio.sleep(10)
        
        media = Bot(
            name=str(data["bot_id"]),
            api_id=data["api_id"],
            api_hash=data["api_hash"],
            bot_token=data["bot_token"]
        )

        mongo = MongoClient(data["mongo_url"])

        media.mongo = mongo
        media.db = mongo[data.get("database", "sharingx")]

        await media.start()

        for mod in loadModule():
            importlib.reload(
                importlib.import_module(
                    f"SharingX.modules.{mod}"
                )
            )
            
        await set_bot_status(bot_id, "running")

    except Exception as e:
        return await callback_query.answer(
            f"❌ {e}",
            show_alert=True
        )

    try:
        await bot_settings(client, callback_query)
    except Exception:
        pass
        
@app.on_callback_query(filters.regex(r"^deletebot_(.+)$"))
async def delete_bot(client, callback_query: CallbackQuery):

    bot_id = callback_query.data.split("_", 1)[1]

    data = await get_bot_data(bot_id)

    if not data:
        return await callback_query.answer(
            "Bot tidak ditemukan.",
            show_alert=True
        )

    try:
        bot = Bot.get_instance(bot_id)

        if bot:
            await bot.stop()

        await remove_bot(bot_id)

        await remove_user_bot(
            callback_query.from_user.id,
            bot_id
        )

        await callback_query.answer(
            "Bot berhasil dihapus.",
            show_alert=True
        )

    except Exception as e:
        return await callback_query.answer(
            str(e),
            show_alert=True
        )

    bots = await get_user_bots(callback_query.from_user.id)

    if not bots:
        return await callback_query.edit_message_text(
            "<b>📦 My Bots</b>\n\n"
            "Anda belum memiliki bot.",
            reply_markup=InlineKeyboardMarkup(
                [
                    [
                        InlineKeyboardButton(
                            "➕ Create Bot",
                            callback_data="create_bot"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "⬅️ Back",
                            callback_data="back_start"
                        )
                    ]
                ]
            )
        )

    buttons = []

    for bot in bots:
        status = bot.get("status", "running")
        emoji = "🟢" if status == "running" else "🔴"

        username = bot.get("username")

        buttons.append(
            [
                InlineKeyboardButton(
                    f"{emoji} @{username}" if username else f"{emoji} {bot['bot_id']}",
                    callback_data=f"bot_{bot['bot_id']}"
                )
            ]
        )

    buttons.append(
        [
            InlineKeyboardButton(
                "⬅️ Back",
                callback_data="back_start"
            )
        ]
    )

    await callback_query.edit_message_text(
        f"<b>📦 My Bots ({len(bots)})</b>\n\n"
        "Silahkan pilih bot yang ingin dikelola.",
        reply_markup=InlineKeyboardMarkup(buttons)
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

    await add_user_bot(
        user_id,
        str(me.id)
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
        
    os.execv(
        sys.executable,
        [sys.executable, "-m", "SharingX"]
    )
    
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
