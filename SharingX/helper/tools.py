import base64
from pyrogram import filters

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
