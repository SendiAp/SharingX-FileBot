import os
import sys
import asyncio
import traceback

from pyromod import listen
from pyrogram import Client
from pyrogram import __version__

from SharingX.config import API_HASH, API_ID, BOT_TOKEN, LOGGER

class Bot(Client):
    def __init__(self):
        super().__init__(
            "Bot",
            api_hash=API_HASH,
            api_id=API_ID,
            plugins={"root": "SharingX/modules"},
            workers=4,
            bot_token=BOT_TOKEN,
        )
        self.LOGGER = LOGGER

    async def start(self):
        try:
            await super().start()
            usr_bot_me = await self.get_me()
            self.username = usr_bot_me.username
            self.namebot = usr_bot_me.first_name
            self.LOGGER(__name__).info(
                f"TG_BOT_TOKEN detected!\n┌ First Name: {self.namebot}\n└ Username: @{self.username}"
            )
        except Exception as a:
            self.LOGGER(__name__).warning(a)
            self.LOGGER(__name__).info(
                "Bot Berhenti."
            )
            sys.exit()
            
bot = Bot()
