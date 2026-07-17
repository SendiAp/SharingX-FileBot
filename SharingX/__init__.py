import time
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
    _instances = {}

    _message_handlers = []
    _callback_handlers = []

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        self.mongo = None
        self.db = None
        self.start_time = None
        
    async def copy(
        self,
        chat_id,
        from_chat_id=None,
        message_id=None,
        message=None,
        **kwargs
    ):
        if message:
            from_chat_id = message.chat.id
            message_id = message.id
            
        return await self.copy_message(
            chat_id=chat_id,
            from_chat_id=from_chat_id,
            message_id=message_id,
            **kwargs
        )
              
    @classmethod
    def on_message(cls, filters=None, group=0):
        def decorator(func):
            cls._message_handlers.append((func, filters, group))

            for bot in cls._bots:
                bot.add_handler(
                    MessageHandler(func, filters),
                    group
                )

            return func

        return decorator

    @classmethod
    def on_callback_query(cls, filters=None, group=0):
        def decorator(func):
            cls._callback_handlers.append((func, filters, group))

            for bot in cls._bots:
                bot.add_handler(
                    CallbackQueryHandler(func, filters),
                    group
                )

            return func

        return decorator

    async def start(self):
        await super().start()

        self.start_time = time.time()

        for func, filters, group in self._message_handlers:
            self.add_handler(
                MessageHandler(func, filters),
                group
            )

        for func, filters, group in self._callback_handlers:
            self.add_handler(
                CallbackQueryHandler(func, filters),
                group
            )

        if self not in self._bots:
            self._bots.append(self)

        if self.me:
            self._instances[str(self.me.id)] = self

    async def stop(self, *args, **kwargs):
        try:
            await super().stop(*args, **kwargs)
        finally:
            if self in self._bots:
                self._bots.remove(self)

            if self.me:
                self._instances.pop(str(self.me.id), None)

            self.start_time = None

    @classmethod
    def get_instance(cls, bot_id):
        return cls._instances.get(str(bot_id))
        
class MainApp(Client):
    def __init__(self):
        super().__init__(
            "MainApp",
            api_id=API_ID,
            api_hash=API_HASH,
            bot_token=BOT_TOKEN,
            plugins=dict(root="SharingX/modules"),
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
                f"TG_BOT_TOKEN detected!\n"
                f"┌ First Name: {me.first_name}\n"
                f"├ ID: {self.id}\n"
                f"└ Username: @{self.username}"
            )

        except Exception as e:
            self.LOGGER(__name__).error(
                f"Gagal start bot utama: {e}"
            )
            sys.exit()


app = MainApp()
