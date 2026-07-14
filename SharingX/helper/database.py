from pymongo import MongoClient
from SharingX.config import MONGO_DB_URL

mongo = MongoClient(MONGO_DB_URL)

db = mongo["sharingx"]
from pymongo import MongoClient

mongo = MongoClient(MONGO_DB_URI)
db = mongo["SharingX"]

forcesubdb = db["forcesub"]

async def add_forcesub(chat_id: int):
    forcesubdb.update_one(
        {"_id": chat_id},
        {"$set": {"chat_id": chat_id}},
        upsert=True
    )

async def get_forcesubs():
    return [x["chat_id"] for x in forcesubdb.find()]

async def del_forcesub(chat_id: int):
    forcesubdb.delete_one({"_id": chat_id})
