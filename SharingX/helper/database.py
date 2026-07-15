from pymongo import MongoClient
from SharingX.config import MONGO_DB_URL

mongo = MongoClient(MONGO_DB_URL)

db = mongo["sharingx"]
forcesubdb = db["forcesub"]

async def add_forcesub(chat_id: int):
    if not forcesubdb.find_one({"chat_id": chat_id}):
        forcesubdb.insert_one({
            "chat_id": chat_id
        })


async def get_forcesubs():
    return [doc["chat_id"] for doc in forcesubdb.find({}, {"chat_id": 1})]


async def del_forcesub(chat_id: int):
    forcesubdb.delete_one({"chat_id": chat_id})
