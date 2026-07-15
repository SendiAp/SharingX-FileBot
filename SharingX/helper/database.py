from pymongo import MongoClient
from SharingX.config import MONGO_DB_URL

mongo = MongoClient(MONGO_DB_URL)

db = mongo["sharingx"]
forcesubdb = db["forcesub"]


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
