from pymongo import MongoClient
from SharingX.config import MONGO_DB_URL

mongo = MongoClient(MONGO_DB_URL)

db = mongo["sharingx"]
forcesub_db = db["forcesub"]


async def _create():
    data = forcesub_db.find_one({"_id": "forcesub"})

    if not data:
        data = {
            "_id": "forcesub",
            "enabled": False,
            "channels": []
        }
        forcesub_db.insert_one(data)

    return data


async def get_forcesub():
    data = await _create()
    return data.get("channels", [])


async def add_forcesub(chat_id):
    data = await _create()

    channels = data.get("channels", [])

    if chat_id in channels:
        return False

    if len(channels) >= 50:
        return False

    channels.append(chat_id)

    forcesub_db.update_one(
        {"_id": "forcesub"},
        {
            "$set": {
                "channels": channels
            }
        },
        upsert=True
    )

    return True


async def del_forcesub(chat_id):
    data = await _create()

    channels = data.get("channels", [])

    if chat_id not in channels:
        return False

    channels.remove(chat_id)

    forcesub_db.update_one(
        {"_id": "forcesub"},
        {
            "$set": {
                "channels": channels
            }
        },
        upsert=True
    )

    return True


async def clear_forcesub():
    forcesub_db.update_one(
        {"_id": "forcesub"},
        {
            "$set": {
                "channels": []
            }
        },
        upsert=True
    )


async def get_force_sub_status():
    data = await _create()
    return data.get("enabled", False)


async def set_force_sub_status(status):
    forcesub_db.update_one(
        {"_id": "forcesub"},
        {
            "$set": {
                "enabled": bool(status)
            }
        },
        upsert=True
    )


async def get_force_sub_count():
    data = await _create()
    return len(data.get("channels", []))


async def is_forcesub(chat_id):
    data = await _create()
    return chat_id in data.get("channels", [])


async def get_force_sub_data():
    return await _create()


async def toggle_force_sub():
    status = await get_force_sub_status()
    await set_force_sub_status(not status)
    return not status


async def remove_all_forcesub():
    forcesub_db.update_one(
        {"_id": "forcesub"},
        {
            "$set": {
                "channels": [],
                "enabled": False
            }
        },
        upsert=True
    )


async def total_forcesub():
    data = await _create()
    return len(data.get("channels", []))
