import sys
import asyncio
import importlib

from SharingX import bot
from pyrogram import idle
from SharingX.config import LOGGER

async def main():
    try:
        await bot.start()
        ex = await bot.get_me()
        LOGGER("INFO").info(f"{ex.first_name} | [ @{ex.username} ] | 🔥 BERHASIL DIAKTIFKAN! 🔥")
        await idle()
    except Exception as a:
        print(a)

if __name__ == "__main__":
    LOGGER("INFO").info("Starting Bot...")
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
