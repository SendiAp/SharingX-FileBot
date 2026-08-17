import re
import base64
import asyncio
from pyrogram import filters

from SharingX.helper.database import get_database_channel

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

async def get_message_id(client, message):
    db = await get_database_channel(client)

    if not db:
        return 0

    if message.forward_from_chat and message.forward_from_chat.id == db:
        return message.forward_from_message_id

    elif message.forward_from_chat or message.forward_sender_name or not message.text:
        return 0

    else:
        pattern = r"https://t.me/(?:c/)?(.*)/(\d+)"
        matches = re.match(pattern, message.text)

        if not matches:
            return 0

        channel_id = matches[1]
        msg_id = int(matches[2])

        if channel_id.isdigit():
            if f"-100{channel_id}" == str(db):
                return msg_id

        elif message.text.startswith("https://t.me/"):
            try:
                chat = await client.get_chat(f"@{channel_id}")

                if chat.id == db:
                    return msg_id
            except:
                pass

    return 0
    
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
