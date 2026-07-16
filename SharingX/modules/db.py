from pymongo.collection import Collection


def _col(client, name: str) -> Collection:
    return client.db[name]


# =========================
# DATABASE CHANNEL
# =========================

async def set_database_channel(client, chat_id: int):
    _col(client, "database_channel").update_one(
        {"_id": "database"},
        {"$set": {"chat_id": chat_id}},
        upsert=True
    )


async def get_database_channel(client):
    data = _col(client, "database_channel").find_one(
        {"_id": "database"}
    )
    return data.get("chat_id") if data else None


async def del_database_channel(client):
    _col(client, "database_channel").delete_one(
        {"_id": "database"}
    )


# =========================
# AUTO LINK
# =========================

async def set_link_status(client, status: bool):
    _col(client, "link_mode").update_one(
        {"_id": "link_mode"},
        {"$set": {"enabled": status}},
        upsert=True
    )


async def get_link_status(client):
    data = _col(client, "link_mode").find_one(
        {"_id": "link_mode"}
    )

    if not data:
        return True

    return data.get("enabled", True)


# =========================
# FORCE SUBSCRIBE
# =========================

async def add_forcesub(client, chat_id: int):
    _col(client, "forcesub").update_one(
        {"_id": chat_id},
        {"$set": {"chat_id": chat_id}},
        upsert=True
    )


async def get_forcesubs(client):
    data = []

    for doc in _col(client, "forcesub").find({}):

        if "chat_id" in doc:
            data.append(doc["chat_id"])

        elif "_id" in doc and isinstance(doc["_id"], int):
            data.append(doc["_id"])

    return data


async def del_forcesub(client, chat_id: int):
    _col(client, "forcesub").delete_one(
        {"_id": chat_id}
    )


# =========================
# BUTTONS
# =========================

async def add_button(client, text: str, url: str):
    _col(client, "buttons").update_one(
        {"text": text},
        {
            "$set": {
                "text": text,
                "url": url
            }
        },
        upsert=True
    )


async def get_buttons(client):
    return list(
        _col(client, "buttons").find(
            {},
            {"_id": 0}
        )
    )


async def del_button(client, text: str):
    _col(client, "buttons").delete_one(
        {"text": text}
    )


# =========================
# SETTINGS
# =========================

async def set_setting(client, key: str, value):
    _col(client, "settings").update_one(
        {"_id": key},
        {"$set": {"value": value}},
        upsert=True
    )


async def get_setting(client, key: str, default=None):
    data = _col(client, "settings").find_one(
        {"_id": key}
    )

    if not data:
        return default

    return data.get("value", default)
