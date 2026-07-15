import sys
import asyncio
from pyromod import listen
from pyrogram import Client
from pyrogram.handlers import MessageHandler, CallbackQueryHandler

from SharingX.logging import LOGGER
from SharingX.config import API_HASH, API_ID, BOT_TOKEN, MONGO_DB_URL

LOOP = asyncio.get_event_loop()

if not API_ID:
    print("API_ID Tidak ada")
    sys.exit()
if not API_HASH:
    print("API_HASH Tidak ada")
    sys.exit()
if not BOT_TOKEN:
    print("BOT_TOKEN Tidak ada")
    sys.exit()
if not MONGO_DB_URL:
    print("MONGO_DB_URL Tidak ada")
    sys.exit()


class Bot(Client):
    _bots = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def on_message(self, filters=None):
        def decorator(func):
            for b in self._bots:
                b.add_handler(MessageHandler(func, filters))
            return func
        return decorator

    def on_callback_query(self, filters=None):
        def decorator(func):
            for b in self._bots:
                b.add_handler(CallbackQueryHandler(func, filters))
            return func
        return decorator

    async def start(self):
        await super().start()
        if self not in self._bots:
            self._bots.append(self)


class MainApp(Client):
    def __init__(self):
        super().__init__(
            "MainApp",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="Media/modules"),
            workers=4,
        )
        self.LOGGER = LOGGER

    async def start(self):
        try:
            await super().start()
            me = await self.get_me()
            self.username = me.username
            self.id = me.id
            self.LOGGER(__name__).info(
                f"TG_BOT_TOKEN detected!\n┌ First Name: {self.id}\n└ Username: @{self.username}"
            )
        except Exception as e:
            self.LOGGER(__name__).error(f"Gagal start bot utama: {e}")
            sys.exit()


app = MainApp()
