import asyncio
import importlib
from pyrogram import idle
from pyrogram.errors import RPCError

from SharingX import LOOP, Bot, app, LOGGER
from SharingX.helper.database import get_bot, remove_bot
from SharingX.modules import loadModule


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
                await b.start()
                LOGGER("Bot").info(f"{b.me.first_name} [🔥 BERHASIL DIAKTIFKAN 🔥]")
            except RPCError:
                await remove_bot(bt["name"])
                LOGGER("Bot").warning(f"🗑️ {bt['name']} Dihapus Dari Database.")
    else:
        LOGGER("Bot").info("⚠️ Bot Multi Client Tidak Ditemukan.")

    for mod in loadModule():
        importlib.reload(importlib.import_module(f"Media.modules.{mod}"))

    LOGGER("Bot").info(f"[🔥 BERHASIL DIAKTIFKAN 🔥]")
    await idle()


if __name__ == "__main__":
    LOOP.run_until_complete(main())
