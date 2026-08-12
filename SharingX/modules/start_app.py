import time
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
    botdb,
    add_bot,
    add_owner,
    remove_bot,
    del_reminder,
    add_reminder,
    add_user_bot,
    get_bot_data,
    get_bot_space,
    get_user_bots,
    set_bot_status,
    remove_user_bot,
    remove_bot_space
)
from SharingX.modules import loadModule

from pyrogram.enums import ButtonStyle

from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton, LinkPreviewOptions

@app.on_message(filters.command("start") & filters.private)
async def start(client, message):
    try:
        await message.reply_text(
            f"👋Hai {message.from_user.first_name}!\n"
            f"<b>SharingX</b> Adalah Bot Yang Dapat Menyimpan Media Yang Anda Kirim Kebot Dan Bot Akan Mengirimkan Link Media/File Tersebut.\n\n"
            f"<b>👉Apa Yang Spesial Disini?</b> Database Tidaklah Sharing Dengan Pengguna Lain, Jadi Anda Dapat Membawa Link Database Anda Sendiri.\n\n"
            f"<b>📚 KLIK PANDUAN APA SAJA REQUEST YANG DIBUTUHKAN 📚</b>\n"
            f"Tekan <b>Bantuan</b> Jika Kalian Belum Mengerti Semua Hal Yang Anda Butuhkan, Jangan Segan Untuk Hubungi <b>Admin</b> Atau <b>Pemilik</b> Jika Butuh Bantuan.\n\n"
            f"<b>📜 Privacy Policy</b>",
            reply_markup = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🤖 Space", callback_data="buy_space"),
                    InlineKeyboardButton("📊 My Bots", callback_data="my_bots")
                ],
                [
                    InlineKeyboardButton("📚 Panduan", callback_data="0"),
                    InlineKeyboardButton("⚠️ Bantuan", callback_data="0")
                ],
                [
                    InlineKeyboardButton("</> Command", callback_data="0")
                ]
            ])
        )
    except Exception as e:
        return await message.reply_text(f"<b>Terjadi Kesalahan:</b> `{str(e)}`")
        
@app.on_callback_query(filters.regex("^back_start$"))
async def back_start(client, callback_query: CallbackQuery):
    try:
        await callback_query.edit_message_text(
            f"👋Hai {callback_query.from_user.first_name}!\n"
            f"<b>SharingX</b> Adalah Bot Yang Dapat Menyimpan Media Yang Anda Kirim Kebot Dan Bot Akan Mengirimkan Link Media/File Tersebut.\n\n"
            f"<b>👉Apa Yang Spesial Disini?</b>, Database Tidaklah Sharing Dengan Pengguna Lain, Jadi Anda Dapat Membawa Link Database Sendiri.\n\n"
            f"<b>📚 KLIK PANDUAN APA SAJA REQUEST YANG DIBUTUHKAN 📚</b>\n"
            f"Tekan <b>Bantuan</b> Jika Kalian Belum Mengerti Semua Hal Yang Anda Butuhkan, Jangan Segan Untuk Hubungi <b>Admin</b> Atau <b>Pemilik</b> Jika Butuh Bantuan.\n\n"
            f"<b>📜 Privacy Policy</b>",
            reply_markup = InlineKeyboardMarkup([
                [
                    InlineKeyboardButton("🤖 Space", callback_data="buy_space"),
                    InlineKeyboardButton("📊 My Bots", callback_data="my_bots")
                ],
                [
                    InlineKeyboardButton("📚 Panduan", callback_data="0"),
                    InlineKeyboardButton("⚠️ Bantuan", callback_data="0")
                ],
                [
                    InlineKeyboardButton("</> Command", callback_data="0")
                ]
            ])
        )
    except Exception as e:
        return await callback_query.edit_message_text(f"<b>Terjadi Kesalahan:</b> `{str(e)}`")

@app.on_callback_query(filters.regex("^my_bots$"))
async def my_bots(client, callback_query: CallbackQuery):
    try:
        user_id = callback_query.from_user.id

        space = await get_bot_space(user_id)
        bots = await get_user_bots(user_id)

        if not bots and space <= 0:
            return await callback_query.edit_message_text(
                "<b>⚠️ Kamu Belum Memiliki Space Bot!</b>\n\n"
                "Untuk membuat bot, kamu harus membeli "
                "<b>Space Bot</b> terlebih dahulu.",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "🛒 Beli Space Bot",
                            callback_data="buy_space"
                        )
                    ],
                    [
                        InlineKeyboardButton(
                            "🔙 Kembali",
                            callback_data="back_start"
                        )
                    ]
                ])
            )

        status_map = {
            "running": ("🟢", "Running"),
            "stopped": ("🔴", "Stopped"),
            "restart": ("🔄", "Restart"),
            "crash": ("⚫", "Crash"),
            "expired": ("⏳", "Expired"),
            "terminated": ("⛔", "Terminated")
        }

        count = {
            "running": 0,
            "stopped": 0,
            "restart": 0,
            "crash": 0,
            "expired": 0,
            "terminated": 0
        }

        buttons = []

        for bot in bots:
            bot_id = str(bot["bot_id"])

            status = bot.get(
                "status",
                "stopped"
            )

            count[status] = count.get(
                status,
                0
            ) + 1

            emoji, text_status = status_map.get(
                status,
                ("⚫", status.title())
            )

            name = bot.get(
                "name",
                bot_id
            )

            try:
                robot = Bot.get_instance(bot_id)

                if robot:
                    me = await robot.get_me()

                    if me.username:
                        name = f"@{me.username}"

            except Exception:
                pass

            buttons.append([
                InlineKeyboardButton(
                    f"{name} | {emoji} {text_status}",
                    callback_data=f"bot_{bot_id}"
                )
            ])
            
        used_space = len(bots)

        if space > used_space:
            buttons.append([
                InlineKeyboardButton(
                    "➕ Create Bot",
                    callback_data="create_bot"
                )
            ])

        if space <= used_space:
            buttons.append([
                InlineKeyboardButton(
                    "🛒 Beli Space Bot",
                    callback_data="buy_space"
                )
            ])

        buttons.append([
            InlineKeyboardButton(
                "🔙 Kembali",
                callback_data="back_start"
            )
        ])

        text = (
            "<b><u>• Daftar Bot dan Space Terdaftar</u></b>\n\n"
            f"<b>• Running |</b> "
            f"{count['running']} bot\n"
            f"<b>• Stopped |</b> "
            f"{count['stopped']} bot\n"
            f"<b>• Restart |</b> "
            f"{count['restart']} bot\n"
            f"<b>• Crash |</b> "
            f"{count['crash']} bot\n"
            f"<b>• Expired |</b> "
            f"{count['expired']} bot\n\n"
            f"<b>• Space |</b> "
            f"<pre>({used_space}/{space})</pre>"
        )

        await callback_query.edit_message_text(
            text,
            reply_markup=InlineKeyboardMarkup(buttons)
        )

    except Exception as e:
        await callback_query.edit_message_text(
            f"<b>Terjadi Kesalahan:</b>\n"
            f"<code>{str(e)}</code>"
        )

@app.on_callback_query(
    filters.regex(r"^bot_logs_(.+)$")
)
async def bot_logs(client, callback_query: CallbackQuery):
    try:
        bot_id = callback_query.data.split(
            "bot_logs_",
            1
        )[1]

        bot = botdb.find_one({
            "bot_id": str(bot_id)
        })

        if not bot:
            return await callback_query.answer(
                "❌ Bot tidak ditemukan.",
                show_alert=True
            )

        error = bot.get(
            "error",
            "Tidak ada informasi error."
        )

        text = (
            "<b>📋 Bot Logs</b>\n"
            "––––—––––———––•\n\n"
            f"<b>🤖 Bot ID:</b> "
            f"<code>{bot_id}</code>\n"
            f"<b>📊 Status:</b> ⚫ Crash\n\n"
            "<b>❌ Error:</b>\n"
            f"<pre>{error}</pre>"
        )

        # Batas aman Telegram
        if len(text) > 4000:
            text = text[:3900] + "\n\n<code>...Log terlalu panjang.</code>"

        await callback_query.edit_message_text(
            text,
            link_preview_options=LinkPreviewOptions(
                is_disabled=True
            ),
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "🔙 Kembali",
                        callback_data=f"bot_{bot_id}"
                    )
                ]
            ])
        )

    except Exception as e:
        await callback_query.answer(
            f"❌ {str(e)}",
            show_alert=True
        )
        
@app.on_callback_query(filters.regex(r"^bot_(.+)$"))
async def bot_settings(client, callback_query: CallbackQuery):
    try:
        bot_id = callback_query.data.split("_", 1)[1]
        data = await get_bot_data(bot_id)

        if not data:
            return await callback_query.answer(
                "⚠️ Bot Tidak Ditemukan!",
                show_alert=True
            )

        status = {
            "running": "🟢 Running",
            "stopped": "🔴 Stopped",
            "restart": "🔄 Restarting",
            "crash": "⚫ Crash"
        }.get(data.get("status"), "⚫ Unknown")

        name = "⚠️ Bot Sedang Offline"
        ping = uptime = "-"
        used = free = docs = cols = 0

        if robot := Bot.get_instance(bot_id):
            me = await robot.get_me()
            name = (
                f"[{me.first_name}](https://t.me/{me.username})"
                if me.username else me.first_name
            )

            t = time.perf_counter()
            await robot.get_me()
            ping_ms = (time.perf_counter() - t) * 1000
            ping_value = round(ping_ms)
            
            if ping_value < 100:
                ping_status = "🟢 Sangat Baik"
            elif ping_value < 200:
                ping_status = "🟢 Baik"
            elif ping_value < 300:
                ping_status = "🟡 Normal"
            elif ping_value < 500:
                ping_status = "🟠 Lambat"
            elif ping_value < 1000:
                ping_status = "🔴 Buruk"
            else:
                ping_status = "🔴 Sangat Buruk"
                
            ping = f"{ping_status} ({ping_value} ms)"

            if robot.start_time:
                s = int(time.time() - robot.start_time)
                h, s = divmod(s, 3600)
                m, s = divmod(s, 60)
                uptime = f"{h:02}<b>Jam</b> {m:02}<b>Menit</b> {s:02}<b>Detik</b>"

            try:
                db = robot.db.command("dbStats")
                cols = db["collections"]
                docs = db["objects"]
            except:
                pass

            buttons = [
                [
                    InlineKeyboardButton(
                        "▶️ Start",
                        callback_data=f"startbot_{bot_id}",
                        style=ButtonStyle.SUCCESS
                    ),
                    InlineKeyboardButton(
                        "⏸ Stop",
                        callback_data=f"stopbot_{bot_id}",
                        style=ButtonStyle.DANGER
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
                        "📋 Logs",
                        callback_data=f"bot_logs_{bot_id}"
                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔗 Putuskan",
                        callback_data=f"deletebot_{bot_id}"

                    )
                ],
                [
                    InlineKeyboardButton(
                        "🔙 Kembali",
                        callback_data="my_bots"
                    )
                ]
            ]
            
            await callback_query.edit_message_text(
                (
                    f"<b><u>• Bot information atau Statistik Bot</u></b>\n"
                    f"––––—––––———––•\n\n"
                    f"🤖 <b><u>Information Bot:</u></b>\n"
                    f"<b><u>• Name</u> |</b> {name}\n"
                    f"<b><u>• ID Bot</u> | </b> <code>{bot_id}</code>\n"
                    f"<b><u>• Status</u> | </b> {status}\n\n"
                    f"🗄️ <b><u>Real-time Sistem:</u></b>\n"
                    f"<b><u>• Ping</u> |</b> {ping}\n"
                    f"<b><u>• Uptime</u> |</b> {uptime}\n\n"
                    f"📂 <b><u>Database Real-time:</u></b>\n"
                    f"<b><u>• Name</u> |</b> {data.get('database')}\n"
                    f"<b><u>• Collection</u> |</b> {cols:,}\n"
                    f"<b><u>• Documents</u> |</b> {docs:,}\n\n"
                    f"<b>© Bot By SharingX</b>"
                ),
                link_preview_options=LinkPreviewOptions(is_disabled=True),
                reply_markup=InlineKeyboardMarkup(buttons)
            )

    except Exception as e:
        return await callback_query.edit_message_text(f"<b>Terjadi Kesalahan:</b> `{str(e)}`")
        
@app.on_callback_query(filters.regex(r"^stopbot_(.+)$"))
async def stop_bot(client, callback_query: CallbackQuery):

    bot_id = callback_query.data.split("_", 1)[1]

    data = await get_bot_data(bot_id)

    if not data:
        return await callback_query.answer("⚠️ Bot Tidak Ditemukan!", show_alert=True)

    bot = Bot.get_instance(bot_id)

    if bot is None:
        await set_bot_status(bot_id, "stopped")

        return await callback_query.answer("🔴 Bot Sudah Berhenti!.", show_alert=True)

    try:
        await bot.stop()
        await set_bot_status(bot_id, "stopped")
        await callback_query.answer("🔴 Bot Berhasil Dihentikan!", show_alert=True)
    except Exception as e:
        return await callback_query.edit_message_text(f"<b>Terjadi Kesalahan:</b> `{str(e)}`")
        
    await bot_settings(client, callback_query)
    
@app.on_callback_query(filters.regex(r"^startbot_(.+)$"))
async def start_bot(client, callback_query: CallbackQuery):

    bot_id = callback_query.data.split("_", 1)[1]

    data = await get_bot_data(bot_id)

    if not data:
        return await callback_query.answer("⚠️ Bot Tidak Ditemukan!", show_alert=True)

    if Bot.get_instance(bot_id):
        return await callback_query.answer("🟢 Bot Sudah Berjalan!", show_alert=True)

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

        await callback_query.answer("🟢 Bot Berhasil Dijalankan!", show_alert=True)

    except Exception as e:
        return await callback_query.edit_message_text(f"<b>Terjadi Kesalahan:</b> `{str(e)}`")

    await bot_settings(client, callback_query)

@app.on_callback_query(filters.regex(r"^restartbot_(.+)$"))
async def restart_bot(client, callback_query: CallbackQuery):

    bot_id = callback_query.data.split("_", 1)[1]

    data = await get_bot_data(bot_id)

    if not data:
        return await callback_query.answer("⚠️ Bot Tidak Ditemukan!")

    old_bot = Bot.get_instance(bot_id)

    if old_bot is None:
        return await callback_query.answer("⚠️ Bot Sedang Tidak Berjalan!")

    try:
        await set_bot_status(bot_id, "restart")

        await callback_query.answer("🔄 Bot Berhasil Direstart!", show_alert=True)

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
        return await callback_query.edit_message_text(f"<b>Terjadi Kesalahan:</b> `{str(e)}`")

    try:
        await bot_settings(client, callback_query)
    except Exception:
        pass
        
@app.on_callback_query(filters.regex(r"^deletebot_(.+)$"))
async def delete_bot(client, callback_query: CallbackQuery):

    bot_id = callback_query.data.split("_", 1)[1]

    data = await get_bot_data(bot_id)

    if not data:
        return await callback_query.answer("⚠️ Bot Tidak Ditemukan!")

    try:
        bot = Bot.get_instance(bot_id)

        if bot:
            await bot.stop()

        await remove_bot(bot_id)
        await del_reminder(str(bot_id))
        await remove_user_bot(callback_query.from_user.id, bot_id)

        await callback_query.edit_message_text(
            "<b>✅ Bot Berhasil Diputuskan!",
            reply_markup=InlineKeyboardMarkup([
                [InlineKeyboardButton("🔙 Kembali", callback_data="back_start")]
            ])
        )

    except Exception as e:
        return await callback_query.edit_message_text(f"<b>Terjadi Kesalahan:</b> `{str(e)}`")

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

    await add_owner(
        str(me.id),
        user_id
    )

    await add_reminder(
        str(media.me.id),
        3
    )
    
    await remove_bot_space(
        user_id,
        1
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
