from pymongo import MongoClient
from SharingX.config import MONGO_DB_URL

mongo = MongoClient(MONGO_DB_URL)
db = mongo["sharingx"]

botdb = db["sharing"]
forcesubdb = db["forcesub"]
linkdb = db["link_settings"]
database_channel = db["database_channel"]

async def get_bot():
    data = []
    async for bt in botdb.find({"bot_id": {"$exists": 1}}):
        data.append(
            dict(
                name=str(bt["bot_id"]),
                api_id=bt["api_id"],
                api_hash=bt["api_hash"],
                bot_token=bt["bot_token"],
            )
        )
    return data

async def add_bot(bot_id, api_id, api_hash, token):
    cek = await botdb.find_one({"bot_id": bot_id})
    if cek:
        await botdb.update_one(
            {"bot_id": bot_id},
            {"$set": {"api_id": api_id, "api_hash": api_hash, "bot_token": token}},
        )
    else:
        await botdb.insert_one(
            {
                "bot_id": bot_id,
                "api_id": api_id,
                "api_hash": api_hash,
                "bot_token": token,
            }
        )

async def remove_bot(bot_id):
    return await botdb.delete_one({"bot_id": bot_id})

async def set_database_channel(chat_id: int):
    database_channel.update_one(
        {"_id": "database"},
        {"$set": {"chat_id": chat_id}},
        upsert=True
    )

async def get_database_channel():
    data = database_channel.find_one({"_id": "database"})
    return data.get("chat_id") if data else None
    
async def set_link_status(status: bool):
    linkdb.update_one(
        {"_id": "link_mode"},
        {"$set": {"enabled": status}},
        upsert=True
    )

async def get_link_status():
    data = linkdb.find_one({"_id": "link_mode"})
    if not data:
        return True
    return data.get("enabled", True)

async def add_forcesub(chat_id: int):
    forcesubdb.update_one(
        {"_id": chat_id},
        {"$set": {"chat_id": chat_id}},
        upsert=True
    )


async def get_forcesubs():
    data = []

    for doc in forcesubdb.find({}):
        if "chat_id" in doc:
            data.append(doc["chat_id"])
        elif "_id" in doc and isinstance(doc["_id"], int):
            data.append(doc["_id"])

    return data


async def del_forcesub(chat_id: int):
    forcesubdb.delete_one({"_id": chat_id})
