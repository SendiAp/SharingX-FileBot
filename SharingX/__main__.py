import asyncio
import importlib

from pyrogram import idle
from pymongo import MongoClient
from pyrogram.errors import RPCError

from SharingX.modules import loadModule
from SharingX import LOOP, Bot, app, LOGGER
from SharingX.modules.reminder_app import expiry_reminder_loop

from SharingX.helper.database import (
    botdb,
    get_bot,
    get_owner,
    remove_bot,
    set_bot_status
)

async def main():
    await app.start()

    asyncio.create_task(
        expiry_reminder_loop()
    )

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

                mongo = MongoClient(
                    bt["mongo_url"]
                )

                b.mongo = mongo
                b.db = mongo[
                    bt.get(
                        "database",
                        "sharingx"
                    )
                ]

                await b.start()

                owner = await get_owner(
                    bt["bot_id"]
                )

                if owner:
                    b.db["owner"].update_one(
                        {},
                        {
                            "$set": {
                                "user_id": owner["user_id"]
                            }
                        },
                        upsert=True
                    )

                LOGGER("Bot").info(
                    f"{b.me.first_name} "
                    f"[🔥 BERHASIL DIAKTIFKAN 🔥]"
                )

            except RPCError:
                await remove_bot(bt["bot_id"])

                LOGGER("Bot").warning(
                    f"🗑️ {bt['bot_id']} Berhasil Dari Database!")

            except Exception as e:
                error_text = str(e)
                LOGGER("Bot").error(f"⛔ Crash Bot, Gagal Running {bt['bot_id']} | {e}")
                botdb.update_one(
                    {
                        "bot_id": str(bt["bot_id"])
                    },
                    {
                        "$set": {
                            "status": "crash",
                            "error": error_text
                        }
                    }
                )
    else:
        LOGGER("Bot").info(
            "⚠️ Tidak Ada Bot Yang Diaktifkan!"
        )

    for mod in loadModule():
        importlib.reload(
            importlib.import_module(
                f"SharingX.modules.{mod}"
            )
        )

    LOGGER("Bot").info(
        "[🔥 BERHASIL DIAKTIFKAN 🔥]"
    )

    await idle()


if __name__ == "__main__":
    LOOP.run_until_complete(main())
