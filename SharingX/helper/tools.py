import base64
import asyncio
from pyrogram import filters

async def get_messages(c, message_ids, database_channel):
    messages = []
    total_messages = 0

    while total_messages != len(message_ids):
        temb_ids = message_ids[
            total_messages : total_messages + 200
        ]

        try:
            msgs = await c.get_messages(
                database_channel,
                temb_ids
            )

        except FloodWait as e:
            await asyncio.sleep(e.value)

            msgs = await c.get_messages(
                database_channel,
                temb_ids
            )

        except BaseException:
            msgs = []

        total_messages += len(temb_ids)
        messages.extend(msgs)

    return messages
    
def strtobool(val):
    return str(val).lower() in ("true", "1", "yes", "y", "on")
    
async def encode(string):
    string_bytes = string.encode("ascii")
    base64_bytes = base64.urlsafe_b64encode(string_bytes)
    return (base64_bytes.decode("ascii")).strip("=")

async def decode(text: str):
    text += "=" * (-len(text) % 4)
    return base64.urlsafe_b64decode(
        text.encode()
    ).decode()
