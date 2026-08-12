from pymongo import MongoClient
from SharingX.config import MONGO_DB_URL
from datetime import datetime, timedelta, timezone


# ==========================================================
# MONGODB CONNECTION
# ==========================================================

mongo = MongoClient(MONGO_DB_URL)

db = mongo["sharingx"]


# ==========================================================
# BOT DATABASE
# ==========================================================

botdb = db["sharing"]

# Semua log aktivitas bot disimpan di sini
bot_logsdb = db["bot_logs"]


# ==========================================================
# BOT EXPIRY
# ==========================================================

async def add_reminder(bot_id, days=30):
    now = datetime.now(timezone.utc)

    bot = botdb.find_one({
        "bot_id": str(bot_id)
    })

    if not bot:
        return False

    expires_at = now + timedelta(days=days)
    grace_until = expires_at + timedelta(days=3)

    botdb.update_one(
        {
            "bot_id": str(bot_id)
        },
        {
            "$set": {
                "expires_at": expires_at,
                "grace_until": grace_until,
                "status": "running",
                "expiry_reminder": False
            }
        }
    )

    return True


async def del_reminder(bot_id):
    return botdb.update_one(
        {
            "bot_id": str(bot_id)
        },
        {
            "$unset": {
                "expires_at": "",
                "grace_until": "",
                "expiry_reminder": ""
            }
        }
    )


async def get_bot_expiry(bot_id):
    return botdb.find_one(
        {
            "bot_id": str(bot_id)
        },
        {
            "_id": 0,
            "bot_id": 1,
            "expires_at": 1,
            "grace_until": 1,
            "status": 1,
            "expiry_reminder": 1
        }
    )


async def set_expiry_reminder(bot_id, status):
    return botdb.update_one(
        {
            "bot_id": str(bot_id)
        },
        {
            "$set": {
                "expiry_reminder": status
            }
        }
    )


# ==========================================================
# BOT DATA
# ==========================================================

async def get_bot():
    data = []

    for bt in botdb.find({
        "bot_id": {
            "$exists": True
        }
    }):
        data.append({
            "name": str(bt["bot_id"]),
            "bot_id": bt["bot_id"],
            "api_id": bt["api_id"],
            "api_hash": bt["api_hash"],
            "bot_token": bt["bot_token"],
            "mongo_url": bt["mongo_url"],
            "database": bt.get(
                "database",
                "sharingx"
            ),
            "status": bt.get(
                "status",
                "running"
            ),
        })

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
        "bot_id": str(bot_id),
        "api_id": api_id,
        "api_hash": api_hash,
        "bot_token": bot_token,
        "mongo_url": mongo_url,
        "database": database,
        "status": "running"
    }

    cek = botdb.find_one({
        "bot_id": str(bot_id)
    })

    if cek:
        botdb.update_one(
            {
                "bot_id": str(bot_id)
            },
            {
                "$set": data
            }
        )
    else:
        botdb.insert_one(data)


async def remove_bot(bot_id):
    return botdb.delete_one({
        "bot_id": str(bot_id)
    })


async def get_bot_data(bot_id):
    bot_id = str(bot_id)

    data = botdb.find_one({
        "bot_id": bot_id
    })

    if data:
        return data

    try:
        return botdb.find_one({
            "bot_id": int(bot_id)
        })
    except (ValueError, TypeError):
        return None


async def set_bot_status(bot_id, status):
    return botdb.update_one(
        {
            "bot_id": str(bot_id)
        },
        {
            "$set": {
                "status": status
            }
        }
    )


# ==========================================================
# BOT LOGS
# ==========================================================

async def add_bot_log(
    bot_id,
    log_type,
    message
):
    """
    Menyimpan log aktivitas bot.

    Contoh type:
    START
    STOP
    RESTART
    RUNNING
    ERROR
    CRASH
    EXPIRED
    DELETE
    """

    return bot_logsdb.insert_one({
        "bot_id": str(bot_id),
        "type": str(log_type).upper(),
        "message": str(message),
        "created_at": datetime.now(timezone.utc)
    })


async def get_bot_logs(
    bot_id,
    limit=20
):
    """
    Mengambil log terbaru.
    """

    return list(
        bot_logsdb.find(
            {
                "bot_id": str(bot_id)
            },
            {
                "_id": 0,
                "bot_id": 1,
                "type": 1,
                "message": 1,
                "created_at": 1
            }
        )
        .sort(
            "created_at",
            -1
        )
        .limit(limit)
    )


async def clear_bot_logs(bot_id):
    """
    Menghapus seluruh log bot.
    """

    return bot_logsdb.delete_many({
        "bot_id": str(bot_id)
    })


async def get_bot_log_count(bot_id):
    """
    Mengambil jumlah log bot.
    """

    return bot_logsdb.count_documents({
        "bot_id": str(bot_id)
    })


# ==========================================================
# MY BOT USERS
# ==========================================================

userbotdb = db["mybot_users"]


async def add_user_bot(
    user_id,
    bot_id
):
    userbotdb.update_one(
        {
            "user_id": user_id
        },
        {
            "$addToSet": {
                "bots": str(bot_id)
            }
        },
        upsert=True
    )


async def remove_user_bot(
    user_id,
    bot_id
):
    return userbotdb.update_one(
        {
            "user_id": user_id
        },
        {
            "$pull": {
                "bots": str(bot_id)
            }
        }
    )


async def get_user_bot_ids(user_id):
    data = userbotdb.find_one({
        "user_id": user_id
    })

    if not data:
        return []

    return data.get(
        "bots",
        []
    )


async def get_user_bots(user_id):
    bot_ids = await get_user_bot_ids(
        user_id
    )

    bots = []

    for bot_id in bot_ids:
        bot = botdb.find_one({
            "bot_id": str(bot_id)
        })

        if bot:
            bots.append(bot)

    return bots


async def get_user_data(user_id):
    return userbotdb.find_one({
        "user_id": user_id
    })


# ==========================================================
# OWNER DATABASE
# ==========================================================

ownerdb = db["owner"]


async def add_owner(
    bot_id,
    user_id
):
    return ownerdb.update_one(
        {
            "bot_id": str(bot_id)
        },
        {
            "$set": {
                "bot_id": str(bot_id),
                "user_id": user_id
            }
        },
        upsert=True
    )


async def get_owner(bot_id):
    return ownerdb.find_one({
        "bot_id": str(bot_id)
    })


async def remove_owner(bot_id):
    return ownerdb.delete_one({
        "bot_id": str(bot_id)
    })


# ==========================================================
# BOT SPACE
# ==========================================================

spacedb = db["bot_space"]


async def init_bot_space(user_id):
    return spacedb.update_one(
        {
            "user_id": user_id
        },
        {
            "$setOnInsert": {
                "user_id": user_id,
                "space": 0
            }
        },
        upsert=True
    )


async def get_bot_space(user_id):
    data = spacedb.find_one({
        "user_id": user_id
    })

    if not data:
        await init_bot_space(user_id)
        return 0

    return data.get(
        "space",
        0
    )


async def set_bot_space(
    user_id,
    space
):
    return spacedb.update_one(
        {
            "user_id": user_id
        },
        {
            "$set": {
                "user_id": user_id,
                "space": max(
                    0,
                    space
                )
            }
        },
        upsert=True
    )


async def add_bot_space(
    user_id,
    amount=1
):
    await init_bot_space(user_id)

    return spacedb.update_one(
        {
            "user_id": user_id
        },
        {
            "$inc": {
                "space": amount
            }
        }
    )


async def remove_bot_space(
    user_id,
    amount=1
):
    await init_bot_space(user_id)

    return spacedb.update_one(
        {
            "user_id": user_id,
            "space": {
                "$gte": amount
            }
        },
        {
            "$inc": {
                "space": -amount
            }
        }
    )


# ==========================================================
# SPACE ORDER
# ==========================================================

space_orderdb = db["space_orders"]


async def set_space_order(
    user_id,
    quantity=1,
    price=45000,
    voucher=None,
    discount=0
):
    total = max(
        0,
        (price * quantity) - discount
    )

    return space_orderdb.update_one(
        {
            "user_id": user_id
        },
        {
            "$set": {
                "user_id": user_id,
                "quantity": quantity,
                "price": price,
                "discount": discount,
                "voucher_used": voucher,
                "total": total,
                "status": "pending"
            }
        },
        upsert=True
    )


async def get_space_order(user_id):
    return space_orderdb.find_one({
        "user_id": user_id
    })


async def set_space_order_status(
    user_id,
    status
):
    return space_orderdb.update_one(
        {
            "user_id": user_id
        },
        {
            "$set": {
                "status": status
            }
        }
    )


async def del_space_order(user_id):
    return space_orderdb.delete_one({
        "user_id": user_id
    })
