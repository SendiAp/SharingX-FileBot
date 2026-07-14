from pymongo import MongoClient
from SharingX.config import MONGO_DB_URL

mongo = MongoClient(MONGO_DB_URL)

db = mongo["SharingX"]
forcesubdb = db["forcesub"]

async def add_forcesub(chat_id: int):
    forcesubdb.update_one(
        {"_id": chat_id},
        {"$set": {"chat_id": chat_id}},
        upsert=True
    )


async def get_forcesubs():
    return [doc["chat_id"] for doc in forcesubdb.find({})]


async def del_forcesub(chat_id: int):
    forcesubdb.delete_one({"_id": chat_id})
