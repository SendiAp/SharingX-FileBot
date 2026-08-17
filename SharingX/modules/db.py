from pymongo.collection import Collection


def _col(client, name: str) -> Collection:
    return client.db[name]


# =========================
# DATABASE CHANNEL (BOT)
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
# AUTO LINK (BOT)
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
# FORCE SUBSCRIBE (BOT)
# =========================

async def add_forcesub(client, chat_id: int):
    _col(client, "forcesub").update_one(
        {"_id": chat_id},
        {"$set": {"chat_id": chat_id}},
        upsert=True
    )


async def get_forcesubs(client):
    data = []

    for doc in _col(client, "forcesub").find({}, {"_id": 1, "chat_id": 1}):
        chat_id = doc.get("chat_id", doc.get("_id"))

        if isinstance(chat_id, int):
            data.append(chat_id)

    return data


async def del_forcesub(client, chat_id: int):
    _col(client, "forcesub").delete_one(
        {"_id": chat_id}
    )


# =========================
# BUTTONS (BOT)
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
# SETTINGS (BOT)
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


# =========================
# MODE BUTTON FORCE SUBSCRIBE (BOT)
# =========================

async def set_forcesub_button_mode(client, mode: str):
    _col(client, "forcesub_settings").update_one(
        {"_id": "button_mode"},
        {"$set": {"mode": mode}},
        upsert=True
    )


async def get_forcesub_button_mode(client):
    data = _col(client, "forcesub_settings").find_one(
        {"_id": "button_mode"}
    )

    if not data:
        return "text"

    mode = data.get("mode", "text")

    if mode not in ("text", "username", "name"):
        return "text"

    return mode


# =========================
# BROADCAST (BOT)
# =========================

async def add_user(client, user_id):
    bot_id = str(client.me.id)

    _col(client, "broad").update_one(
        {
            "bot_id": bot_id,
            "user_id": user_id
        },
        {
            "$set": {
                "bot_id": bot_id,
                "user_id": user_id
            }
        },
        upsert=True
    )


async def get_user(client):
    bot_id = str(client.me.id)

    return [
        doc["user_id"]
        for doc in _col(client, "broad").find(
            {"bot_id": bot_id},
            {
                "_id": 0,
                "user_id": 1
            }
        )
    ]


async def del_user(client, user_id):
    bot_id = str(client.me.id)

    _col(client, "broad").delete_one(
        {
            "bot_id": bot_id,
            "user_id": user_id
        }
    )


# =========================
# PROTECTION (BOT)
# =========================

async def add_protect(client, protect: bool):
    _col(client, "protect").update_one(
        {"_id": "protect"},
        {"$set": {"enabled": protect}},
        upsert=True
    )


async def protect_info(client):
    data = _col(client, "protect").find_one(
        {"_id": "protect"}
    )

    if not data:
        return True

    return data.get("enabled", True)
    

# =========================
# OWNER (BOT)
# =========================

async def add_owner(client, user_id):
    _col(client, "owner").update_one(
        {},
        {
            "$set": {
                "user_id": user_id
            }
        },
        upsert=True
    )


async def get_owner(client):
    data = _col(client, "owner").find_one({})

    return data["user_id"] if data else None


async def is_owner(client, user_id):
    return await get_owner(client) == user_id


async def get_owners(client):
    data = []

    for doc in _col(client, "owner").find({}, {"_id": 0, "user_id": 1}):
        if "user_id" in doc:
            data.append(doc["user_id"])

    return data


# =========================
# ADMIN (BOT)
# =========================

async def add_admin(client, user_id):
    _col(client, "admin").update_one(
        {"user_id": user_id},
        {
            "$set": {
                "user_id": user_id
            }
        },
        upsert=True
    )


async def del_admin(client, user_id):
    _col(client, "admin").delete_one(
        {"user_id": user_id}
    )


async def is_admin(client, user_id):
    data = _col(client, "admin").find_one(
        {"user_id": user_id}
    )

    return data is not None


async def get_admins(client):
    data = []

    for doc in _col(client, "admin").find({}, {"_id": 0, "user_id": 1}):
        if "user_id" in doc:
            data.append(doc["user_id"])

    return data
