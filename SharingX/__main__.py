import asyncio
import importlib

from pyrogram import idle
from pymongo import MongoClient
from pyrogram.errors import RPCError

from SharingX.modules import loadModule
from SharingX import LOOP, Bot, app, LOGGER
from SharingX.helper.database import get_bot, remove_bot

async def main():
    await app.start()

    bots = await get_bot()

    if bots:
        for bt in bots:
            try:
                b = Bot(
                    name=bt["name"],
                    api_id=bt["api_id"],
                    api_hash=bt["api_hash"],
                    bot_token=bt["bot_token"]
                )

                mongo = MongoClient(bt["mongo_url"])
                b.mongo = mongo
                b.db = mongo[bt.get("database", "sharingx")]

                await b.start()

                LOGGER("Bot").info(
                    f"{b.me.first_name} [🔥 BERHASIL DIAKTIFKAN 🔥]"
                )

            except RPCError:
                await remove_bot(bt["bot_id"])
                LOGGER("Bot").warning(
                    f"🗑️ {bt['bot_id']} Dihapus Dari Database."
                )

            except Exception as e:
                LOGGER("Bot").error(
                    f"Gagal Menjalankan Bot {bt['bot_id']} : {e}"
                )
    else:
        LOGGER("Bot").info(
            "⚠️ Bot Multi Client Tidak Ditemukan."
        )

    for mod in loadModule():
        importlib.reload(
            importlib.import_module(f"SharingX.modules.{mod}")
        )

    LOGGER("Bot").info("[🔥 BERHASIL DIAKTIFKAN 🔥]")

    await idle()


if __name__ == "__main__":
    LOOP.run_until_complete(main())
