import asyncio

from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, timezone

from SharingX import app, Bot, LOGGER

from SharingX.helper.database import (
    botdb,
    ownerdb,
    userbotdb,
    set_expiry_reminder
)

# ==========================
# EXPIRY LOOP
# ==========================

async def expiry_reminder_loop():
    while True:
        try:
            await check_expiry_reminder()
            await check_expired_bots()
            await check_terminate_bots()

        except Exception as e:
            LOGGER("Expiry").error(
                f"[EXPIRY LOOP ERROR] {e}"
            )

        await asyncio.sleep(60)


# ==========================
# CHECK EXPIRED BOT
# ==========================

async def check_expired_bots():
    now = datetime.now(timezone.utc)

    bots = botdb.find({
        "expires_at": {
            "$exists": True
        },
        "status": "running"
    })

    for bot in bots:
        bot_id = str(bot["bot_id"])
        expires_at = bot.get("expires_at")

        if not expires_at:
            continue

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        if now < expires_at:
            continue

        await notify_bot_expired(bot_id)

        try:
            robot = Bot.get_instance(bot_id)

            if robot:
                await robot.stop()

        except Exception as e:
            LOGGER("Expiry").error(
                f"[EXPIRED STOP ERROR] {bot_id}: {e}"
            )

        botdb.update_one(
            {
                "bot_id": bot_id,
                "status": "running"
            },
            {
                "$set": {
                    "status": "expired"
                }
            }
        )

# ==========================
# CHECK REMINDER
# ==========================

async def check_expiry_reminder():
    now = datetime.now(timezone.utc)

    bots = botdb.find({
        "expires_at": {
            "$exists": True
        },
        "status": "running"
    })

    for bot in bots:
        bot_id = str(bot["bot_id"])

        expires_at = bot.get("expires_at")

        if not expires_at:
            continue

        if expires_at.tzinfo is None:
            expires_at = expires_at.replace(
                tzinfo=timezone.utc
            )

        reminder_level = bot.get(
            "expiry_reminder_level",
            0
        )

        reminder_targets = {
            1: expires_at - timedelta(days=3),
            2: expires_at - timedelta(days=2),
            3: expires_at - timedelta(days=1)
        }

        next_level = reminder_level + 1

        if next_level not in reminder_targets:
            continue

        target_time = reminder_targets[next_level]

        if now < target_time:
            continue

        if now >= expires_at:
            continue

        owner = ownerdb.find_one({
            "bot_id": bot_id
        })

        if not owner:
            continue

        owner_id = owner.get("user_id")

        if not owner_id:
            continue

        try:
            user = await app.get_users(owner_id)
            mention = user.mention

        except Exception:
            mention = f"<code>{owner_id}</code>"

        expires_text = (
            expires_at
            .astimezone(
                ZoneInfo("Asia/Jakarta")
            )
            .strftime(
                "%d-%m-%Y %H:%M:%S WIB"
            )
        )

        grace_until = bot.get("grace_until")

        if grace_until:
            if grace_until.tzinfo is None:
                grace_until = grace_until.replace(
                    tzinfo=timezone.utc
                )

            terminate_text = (
                grace_until
                .astimezone(
                    ZoneInfo("Asia/Jakarta")
                )
                .strftime(
                    "%d-%m-%Y %H:%M:%S WIB"
                )
            )

        else:
            terminate_text = "-"

        reminder_text = {
            1: "H-3",
            2: "H-2",
            3: "H-1"
        }.get(
            next_level,
            "Reminder"
        )

        text = (
            f"<b><u>Hai, {mention} 👋</u></b>\n\n"
            f"__Kami ingin mengingatkan bahwa bot yang anda sewa "
            f"saat ini akan segera jatuh tempo.__\n\n"

            f"<b>⏰ Reminder {reminder_text}</b>\n\n"

            f"<b><u>🤖 Information Bot:</u></b>\n"
            f"<b><u>• ID |</u></b> <code>{bot_id}</code>\n"
            f"<b><u>• Expired |</u></b> {expires_text}\n"
            f"<b><u>• Terminate |</u></b> {terminate_text}\n\n"

            "🛑 Jika pembayaran tidak dilakukan sebelum jatuh tempo, "
            "bot anda akan dihentikan sementara.\n"

            "⛔ Jika lewat dari tanggal terminate, "
            "data anda berisiko dihapus secara permanen.\n\n"

            "💳 Segera lakukan pembayaran untuk memastikan bot "
            "anda tetap aktif dan data anda masih aman.\n\n"

            "<b>Terimakasih Atas Kerjasamanya, Team SharingX 🙌</b>"
        )

        try:
            await app.send_message(
                owner_id,
                text
            )

        except Exception as e:
            LOGGER("Expiry").warning(
                f"[APP REMINDER ERROR] "
                f"{bot_id}: {e}"
            )

        try:
            robot = Bot.get_instance(bot_id)

            if robot:
                await robot.send_message(
                    owner_id,
                    text
                )

        except Exception as e:
            LOGGER("Expiry").warning(
                f"[BOT REMINDER ERROR] "
                f"{bot_id}: {e}"
            )

        botdb.update_one(
            {
                "bot_id": bot_id
            },
            {
                "$set": {
                    "expiry_reminder_level": next_level
                }
            }
        )

        LOGGER("Expiry").info(
            f"[REMINDER {reminder_text}] "
            f"Bot {bot_id} | "
            f"Expired: {expires_text}"
        )
        
# ==========================
# NOTIFY EXPIRED
# ==========================

async def notify_bot_expired(bot_id):
    bot_id = str(bot_id)

    bot = botdb.find_one({
        "bot_id": bot_id
    })

    if not bot:
        return False

    owner = ownerdb.find_one({
        "bot_id": bot_id
    })

    if not owner:
        return False

    owner_id = owner.get("user_id")
    mention = (await app.get_users(owner_id)).mention
    
    if not owner_id:
        return False

    expires_at = bot.get("expires_at")
    grace_until = bot.get("grace_until")

    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if grace_until and grace_until.tzinfo is None:
        grace_until = grace_until.replace(
            tzinfo=timezone.utc
        )

    expires_text = (
        expires_at
        .astimezone(
            ZoneInfo("Asia/Jakarta")
        )
        .strftime(
            "%d-%m-%Y %H:%M:%S WIB"
        )
        if expires_at
        else "-"
    )

    grace_text = (
        grace_until
        .astimezone(
            ZoneInfo("Asia/Jakarta")
        )
        .strftime(
            "%d-%m-%Y %H:%M:%S WIB"
        )
        if grace_until
        else "-"
    )

    text = (
        f"<b><u>Hai, {mention} 👋</u></b>\n\n"
        f"__Kami ingin menginformasikan bahwa bot anda telah dihentikan sementara, karena anda belum melakukan perpanjangan pada bot.__\n\n"
        f"<b><u>🤖 Information Bot:</u></b>\n"
        f"<b><u>• ID |</u></b> `{bot_id}`\n"
        f"<b><u>• Expired |</u></b> {expires_text}\n"
        f"<b><u>• Terminate |</u></b> {grace_text}\n\n"
        "💳 Kami akan memberikan waktu 3 hari untuk melakukan perpanjangan, kalau tidak bot anda akan dihentikan secara permanen.\n"
        "⛔ Semua data akan terhapus ketika bot melati tanggal terminate, segera lakukan pembayaran.\n"
        "<b>Terimakasih Atas Kerjasamanya, Team SharingX 🙌</b>"
    )

    try:
        await app.send_message(
            owner_id,
            text
        )

    except Exception as e:
        LOGGER("Expiry").warning(
            f"[APP EXPIRED NOTIFY ERROR] "
            f"{bot_id}: {e}"
        )
        
    try:
        robot = Bot.get_instance(bot_id)

        if robot:
            await robot.send_message(
                owner_id,
                text
            )

    except Exception as e:
        LOGGER("Expiry").warning(
            f"[BOT EXPIRED NOTIFY ERROR] "
            f"{bot_id}: {e}"
        )

    return True


# ==========================
# RENEW BOT
# ==========================

async def renew_bot(bot_id, days=30):
    bot_id = str(bot_id)

    now = datetime.now(timezone.utc)

    bot = botdb.find_one({
        "bot_id": bot_id
    })

    if not bot:
        return False

    if bot.get("status") not in [
        "running",
        "expired"
    ]:
        return False

    expires_at = bot.get("expires_at")

    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if expires_at and expires_at > now:
        new_expires_at = (
            expires_at +
            timedelta(days=days)
        )
    else:
        new_expires_at = (
            now +
            timedelta(days=days)
        )

    new_grace_until = (
        new_expires_at +
        timedelta(days=3)
    )

    result = botdb.update_one(
        {
            "bot_id": bot_id,
            "status": {
                "$in": [
                    "running",
                    "expired"
                ]
            }
        },
        {
            "$set": {
                "expires_at": new_expires_at,
                "grace_until": new_grace_until,
                "status": "running",
                "expiry_reminder_level": 0
            }
        }
    )

    return result.modified_count > 0

# ==========================
# RESTART RENEWED BOT
# ==========================

async def restart_renewed_bot(bot_id):
    bot_id = str(bot_id)

    bot_data = botdb.find_one({
        "bot_id": bot_id
    })

    if not bot_data:
        return False

    try:
        robot = Bot.get_instance(bot_id)

        if not robot:
            return False

        await robot.start()

        return True

    except Exception as e:
        LOGGER("Expiry").error(
            f"[RENEW BOT START ERROR] "
            f"{bot_id}: {e}"
        )

        return False

# ==========================
# TERMINATE BOT
# ==========================

async def check_terminate_bots():
    now = datetime.now(timezone.utc)

    bots = botdb.find({
        "status": "expired",
        "grace_until": {
            "$exists": True
        }
    })

    for bot in bots:
        bot_id = str(bot["bot_id"])

        grace_until = bot.get(
            "grace_until"
        )

        if not grace_until:
            continue

        if grace_until.tzinfo is None:
            grace_until = grace_until.replace(
                tzinfo=timezone.utc
            )

        if now < grace_until:
            continue

        owner = ownerdb.find_one({
            "bot_id": bot_id
        })

        owner_id = (
            owner.get("user_id")
            if owner
            else None
        )

        mention = (await app.get_users(owner_id)).mention
        
        try:
            robot = Bot.get_instance(
                bot_id
            )

            if robot:
                try:
                    await robot.stop()

                except Exception:
                    pass

        except Exception:
            pass

        if owner_id:

            text = (
                f"<b><u>Hai, {mention} 👋</u></b>\n\n"
                f"__Kami ingin menginformasikan bahwa bot anda telah terminate, semua data sudah terhapus dalam database kami, tapi jangan kwatir.\n\n"
                f"<b><u>🤖 Information Bot:</u></b>\n"
                f"<b><u>• ID |</u></b> `{bot_id}`\n\n"
                "<u>× Kami sarankan anda dapat membeli space lagi untuk menjalankan bot anda.</u>\n"
                "<u>× Kami tidak menghapus data dari database anda, asalkan anda hafal nama database anda pertama anda buat.</u>\n"
                "<u>× Data anda akan aman, ketika anda membuat bot baru lagi dilayanan kami.</u>\n\n"
                "<b>Terimakasih Atas Kerjasamanya, Team SharingX 🙌</b>"
            )

            try:
                await app.send_message(
                    owner_id,
                    text
                )

            except Exception as e:
                LOGGER("Expiry").warning(
                    f"[TERMINATE NOTIFY ERROR] "
                    f"{bot_id}: {e}"
                )

        # ==========================
        # REMOVE FROM USER BOT
        # ==========================

        userbotdb.update_many(
            {
                "bots": bot_id
            },
            {
                "$pull": {
                    "bots": bot_id
                }
            }
        )

        # ==========================
        # REMOVE OWNER INDUK
        # ==========================

        ownerdb.delete_one({
            "bot_id": bot_id
        })

        # ==========================
        # REMOVE BOT INDUK
        # ==========================

        botdb.delete_one({
            "bot_id": bot_id
        })

        LOGGER("Expiry").info(
            f"Bot {bot_id} berhasil "
            f"di-terminate."
        )
