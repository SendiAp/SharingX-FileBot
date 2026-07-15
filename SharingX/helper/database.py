from pymongo import MongoClient
from SharingX.config import MONGO_DB_URL

mongo = MongoClient(MONGO_DB_URL)
db = mongo["sharingx"]

botdb = db["sharing"]


async def get_bot():
    data = []

    async for bt in botdb.find({"bot_id": {"$exists": True}}):
        data.append(
            {
                "name": str(bt["bot_id"]),
                "bot_id": bt["bot_id"],
                "api_id": bt["api_id"],
                "api_hash": bt["api_hash"],
                "bot_token": bt["bot_token"],
                "mongo_url": bt["mongo_url"],
                "database": bt.get("database", "sharingx"),
            }
        )

    return data


async def add_bot(
    bot_id,
    api_id,
    api_hash,
    bot_token,
    mongo_url,
    database="sharingx",
):
    data = {
        "bot_id": bot_id,
        "api_id": api_id,
        "api_hash": api_hash,
        "bot_token": bot_token,
        "mongo_url": mongo_url,
        "database": database,
    }

    cek = await botdb.find_one({"bot_id": bot_id})

    if cek:
        await botdb.update_one(
            {"bot_id": bot_id},
            {"$set": data},
        )
    else:
        await botdb.insert_one(data)


async def remove_bot(bot_id):
    return await botdb.delete_one({"bot_id": bot_id})


async def get_bot_data(bot_id):
    return await botdb.find_one({"bot_id": bot_id})
