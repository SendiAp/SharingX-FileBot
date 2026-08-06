import base64
from pyrogram import filters
from SharingX.helper.database import is_owner, is_admin

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

async def owner_admin_filter(_, client, message):
    user_id = message.from_user.id

    if await is_owner(client, user_id):
        return True

    if await is_admin(client, user_id):
        return True

    return False

owner_admin = filters.create(owner_admin_filter)
