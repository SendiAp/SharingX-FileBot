from pymongo import MongoClient
from SharingX.config import MONGO_DB_URL

mongo = MongoClient(MONGO_DB_URL)

db = mongo["sharingx"]

botdb = db["sharing"]
userbotdb = db["mybot_users"]

async def get_bot():
    data = []

    for bt in botdb.find({"bot_id": {"$exists": True}}):
        data.append(
            {
                "name": str(bt["bot_id"]),
                "bot_id": bt["bot_id"],
                "api_id": bt["api_id"],
                "api_hash": bt["api_hash"],
                "bot_token": bt["bot_token"],
                "mongo_url": bt["mongo_url"],
                "database": bt.get("database", "sharingx"),
                "status": bt.get("status", "running"),
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
        "status": "running"
    }

    cek = botdb.find_one({"bot_id": bot_id})

    if cek:
        botdb.update_one(
            {"bot_id": bot_id},
            {"$set": data},
        )
    else:
        botdb.insert_one(data)

async def remove_bot(bot_id):
    return botdb.delete_one({"bot_id": bot_id})

async def get_bot_data(bot_id):
    return botdb.find_one({"bot_id": bot_id})

# ==========================
# MY BOT USERS
# ==========================

async def add_user_bot(user_id, bot_id):
    userbotdb.update_one(
        {"user_id": user_id},
        {
            "$addToSet": {
                "bots": str(bot_id)
            }
        },
        upsert=True
    )

async def remove_user_bot(user_id, bot_id):
    userbotdb.update_one(
        {"user_id": user_id},
        {
            "$pull": {
                "bots": str(bot_id)
            }
        }
    )

async def get_user_bot_ids(user_id):
    data = userbotdb.find_one(
        {"user_id": user_id}
    )

    if not data:
        return []

    return data.get("bots", [])

async def get_user_bots(user_id):
    bot_ids = await get_user_bot_ids(user_id)

    bots = []

    for bot_id in bot_ids:
        bot = botdb.find_one({"bot_id": str(bot_id)})

        if bot:
            bots.append(bot)

    return bots

async def get_user_data(user_id):
    return userbotdb.find_one(
        {"user_id": user_id}
    )

async def set_bot_status(bot_id, status):
    return botdb.update_one(
        {"bot_id": str(bot_id)},
        {
            "$set": {
                "status": status
            }
        }
    )
