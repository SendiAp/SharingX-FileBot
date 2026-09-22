import asyncio
import importlib

from pymongo import MongoClient

from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton,
    CallbackQuery
)

from SharingX import app, Bot
from SharingX.helper.database import (
    botdb,
    get_bot_data,
    set_bot_status
)
from SharingX.modules import loadModule
from SharingX.modules.start1_app import bot_settings


@app.on_callback_query(filters.regex(r"^config_(.+)$"))
async def bot_config(client, callback_query):
    bot_id = callback_query.data.split("_", 1)[1]

    data = await get_bot_data(bot_id)

    if not data:
        return await callback_query.answer(
            "⚠️ Bot Tidak Ditemukan!",
            show_alert=True
        )

    text = (
        "<b>⚙️ Bot Configuration</b>\n"
        "––––—––––———––•\n\n"
        "<pre>"
        "{\n"
        f'  "api_id": "{data.get("api_id", "")}",\n'
        f'  "api_hash": "{data.get("api_hash", "")}",\n'
        f'  "bot_token": "{data.get("bot_token", "")}",\n'
        f'  "mongo_url": "{data.get("mongo_url", "")}"\n'
        "}"
        "</pre>"
    )

    await callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🔙 Kembali",
                    callback_data=f"bot_{bot_id}"
                )
            ]
        ])
    )


@app.on_callback_query(filters.regex(r"^stopbot_(.+)$"))
async def stop_bot(client, callback_query: CallbackQuery):
    bot_id = callback_query.data.split("_", 1)[1]

    data = await get_bot_data(bot_id)

    if not data:
        return await callback_query.answer(
            "⚠️ Bot Tidak Ditemukan!",
            show_alert=True
        )

    bot = Bot.get_instance(bot_id)

    if bot is None:
        status = data.get(
            "status",
            "stopped"
        )

        if status == "expired":
            return await callback_query.answer(
                "⚠️ Kamu Memiliki Masa Sewa Yang Jatuh Tempo, Bot Sudah Terhenti Silahkan Melakukan Perpanjangan.",
                show_alert=True
            )

        if status == "crash":
            return await callback_query.answer(
                "⚫ Bot Anda Sudah Terhenti, Karena Crash Kegagalan Menjalankan Bot, Periksa Log Lalu Lapor Ke Developer.",
                show_alert=True
            )

        await set_bot_status(
            bot_id,
            "stopped"
        )

        return await callback_query.answer(
            "🔴 Bot Sudah Berhenti!",
            show_alert=True
        )

    try:
        await bot.stop()

        await set_bot_status(
            bot_id,
            "stopped"
        )

        await callback_query.answer(
            "🔴 Bot Berhasil Dihentikan!",
            show_alert=True
        )

    except Exception as e:
        return await callback_query.edit_message_text(
            f"<b>Terjadi Kesalahan:</b>\n"
            f"<code>{str(e)}</code>"
        )

    await bot_settings(
        client,
        callback_query
    )


@app.on_callback_query(filters.regex(r"^startbot_(.+)$"))
async def start_bot(client, callback_query: CallbackQuery):
    bot_id = callback_query.data.split("_", 1)[1]

    data = await get_bot_data(bot_id)

    if not data:
        return await callback_query.answer(
            "⚠️ Bot Tidak Ditemukan!",
            show_alert=True
        )

    status = data.get(
        "status",
        "stopped"
    )

    if status == "expired":
        return await callback_query.answer(
            "⚠️ Kamu Tidak Bisa Menjalankan Bot Ini, Karena Kamu Memiliki Masa Sewa Bot Yang Telah Jatuh Tempo, Silahkan Lakukan Perpanjangan, Sebelum Bot Terminate.",
            show_alert=True
        )

    if status == "crash":
        return await callback_query.answer(
            "⚫ Kamu Tidak Bisa Menjalankan Bot Ini, Karena Bot Ini Telah Crash Atau Bot Error Tidak Dapat Dijalankan, Silahkan Lihat Log, Lalu Dapat Menghubungi Developer.",
            show_alert=True
        )

    if Bot.get_instance(bot_id):
        return await callback_query.answer(
            "🟢 Bot Sudah Berjalan!",
            show_alert=True
        )

    try:
        media = Bot(
            name=str(data["bot_id"]),
            api_id=data["api_id"],
            api_hash=data["api_hash"],
            bot_token=data["bot_token"]
        )

        mongo = MongoClient(
            data["mongo_url"]
        )

        media.mongo = mongo
        media.db = mongo[
            data.get(
                "database",
                "sharingx"
            )
        ]

        await media.start()

        for mod in loadModule():
            importlib.reload(
                importlib.import_module(
                    f"SharingX.modules.{mod}"
                )
            )

        await set_bot_status(
            bot_id,
            "running"
        )

        await callback_query.answer(
            "🟢 Bot Berhasil Dijalankan!",
            show_alert=True
        )

    except Exception as e:
        await set_bot_status(
            bot_id,
            "crash"
        )

        return await callback_query.edit_message_text(
            f"<b>Terjadi Kesalahan:</b>\n"
            f"<code>{str(e)}</code>"
        )

    await bot_settings(
        client,
        callback_query
    )


@app.on_callback_query(filters.regex(r"^restartbot_(.+)$"))
async def restart_bot(client, callback_query: CallbackQuery):
    bot_id = callback_query.data.split("_", 1)[1]

    data = await get_bot_data(bot_id)

    if not data:
        return await callback_query.answer(
            "⚠️ Bot Tidak Ditemukan!",
            show_alert=True
        )

    status = data.get(
        "status",
        "stopped"
    )

    if status == "expired":
        return await callback_query.answer(
            "⚠️ Kamu Tidak Bisa Merestart Bot Ini, Karena Kamu Memiliki Masa Sewa Bot Yang Telah Jatuh Tempo, Silahkan Lakukan Perpanjangan, Sebelum Bot Terminate.",
            show_alert=True
        )

    if status == "crash":
        return await callback_query.answer(
            "⚫ Kamu Tidak Bisa Merestart Bot Ini, Karena Bot Ini Telah Crash Atau Bot Error Tidak Dapat Dijalankan, Silahkan Lihat Log, Lalu Dapat Menghubungi Developer.",
            show_alert=True
        )

    old_bot = Bot.get_instance(
        bot_id
    )

    if old_bot is None:
        return await callback_query.answer(
            "⚠️ Bot Sedang Tidak Berjalan!",
            show_alert=True
        )

    try:
        await set_bot_status(
            bot_id,
            "restart"
        )

        await callback_query.answer(
            "🔄 Bot Berhasil Direstart!",
            show_alert=True
        )

        await bot_settings(
            client,
            callback_query
        )

        await old_bot.stop()

        await asyncio.sleep(10)

        media = Bot(
            name=str(data["bot_id"]),
            api_id=data["api_id"],
            api_hash=data["api_hash"],
            bot_token=data["bot_token"]
        )

        mongo = MongoClient(
            data["mongo_url"]
        )

        media.mongo = mongo
        media.db = mongo[
            data.get(
                "database",
                "sharingx"
            )
        ]

        await media.start()

        for mod in loadModule():
            importlib.reload(
                importlib.import_module(
                    f"SharingX.modules.{mod}"
                )
            )

        await set_bot_status(
            bot_id,
            "running"
        )

    except Exception as e:
        await set_bot_status(
            bot_id,
            "crash"
        )

        return await callback_query.edit_message_text(
            f"<b>Terjadi Kesalahan:</b>\n"
            f"<code>{str(e)}</code>"
        )

    try:
        await bot_settings(
            client,
            callback_query
        )
    except Exception:
        pass

@app.on_callback_query(filters.regex(r"^settings_(.+)$"))
async def bot_settings_menu(client, callback_query):
    bot_id = callback_query.data.split("_", 1)[1]

    data = await get_bot_data(bot_id)

    if not data:
        return await callback_query.answer(
            "⚠️ Bot Tidak Ditemukan!",
            show_alert=True
        )

    await callback_query.edit_message_text(
        "<b>⚙️ Bot Settings</b>\n"
        "––––—––––———––•\n\n"
        "Silahkan pilih pengaturan yang ingin kamu ubah.",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "✏️ Change Name (Database)",
                    callback_data=f"change_name_{bot_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "👤 Transfer Ownership",
                    callback_data=f"transfer_{bot_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Kembali",
                    callback_data=f"bot_{bot_id}"
                )
            ]
        ])
    )


@app.on_callback_query(filters.regex(r"^change_name_(.+)$"))
async def change_name_warning(client, callback_query):
    bot_id = callback_query.data.split("_", 2)[2]

    data = await get_bot_data(bot_id)

    if not data:
        return await callback_query.answer(
            "⚠️ Bot Tidak Ditemukan!",
            show_alert=True
        )

    current_name = data.get(
        "database",
        "sharingx"
    )

    await callback_query.edit_message_text(
        "<b>⚠️ Peringatan</b>\n\n"
        "Apa Kamu Yakin Ingin Mengganti Nama Database Kamu?\n\n"
        "Semua Data Sebelum Nya Akan Hilang, Jika Anda "
        "Pergunakan Name Sekarang Lagi, Data Akan Pulih Kembali.\n\n"
        f"<b>Database Sekarang:</b> "
        f"<code>{current_name}</code>",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "✅ Ya, Lanjutkan",
                    callback_data=f"chg_name_confirm_{bot_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "❌ Batal",
                    callback_data=f"settings_{bot_id}"
                )
            ]
        ])
    )

@app.on_callback_query(filters.regex(r"^chg_name_confirm_(.+)$"))
async def change_name_confirm(client, callback_query):
    bot_id = callback_query.matches[0].group(1)

    data = await get_bot_data(bot_id)

    if not data:
        return await callback_query.answer(
            "⚠️ Bot Tidak Ditemukan!",
            show_alert=True
        )

    current_name = data.get("database", "sharingx")

    try:
        reply = await callback_query.edit_message_text(
            callback_query.from_user.id,
            "<b>✏️ Silahkan Kirim Nama Database Baru.</b>\n\n"
            "Maksimal <b>30 karakter</b>.",
            filters=filters.text
        )
    except Exception:
        return

    if not reply.text:
        return await reply.reply(
            "❌ <b>Nama Database Tidak Boleh Kosong.</b>"
        )

    if reply.text.startswith("/"):
        await reply.delete()
        return await callback_query.message.reply(
            "<b>❌ Proses dibatalkan.</b>"
        )

    new_name = reply.text.strip()

    if len(new_name) > 30:
        return await reply.reply(
            "❌ <b>Nama Database Maksimal 30 Karakter.</b>"
        )

    if "\x00" in new_name:
        return await reply.reply(
            "❌ <b>Nama Database Tidak Valid.</b>"
        )

    if new_name == current_name:
        return await reply.reply(
            "⚠️ <b>Nama Database Baru Sama Dengan Nama Database Sekarang.</b>"
        )

    result = botdb.update_one(
        {"bot_id": bot_id},
        {"$set": {"database": new_name}}
    )

    if result.modified_count == 0:
        return await reply.reply(
            "❌ <b>Gagal Mengubah Nama Database.</b>"
        )

    await reply.edit(
        "<b>✅ Nama Database Berhasil Diubah!</b>\n\n"
        f"<b>Database Lama:</b> <code>{current_name}</code>\n"
        f"<b>Database Baru:</b> <code>{new_name}</code>\n\n"
        "Data pada database lama tidak dihapus. "
        "Jika kamu menggunakan kembali nama database lama, "
        "data tersebut akan dapat digunakan kembali."
    )

    await bot_settings(client, callback_query)
