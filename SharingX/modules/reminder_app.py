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

        # ==========================
        # NOTIFICATION
        # ==========================

        await notify_bot_expired(bot_id)

        # ==========================
        # STOP BOT
        # ==========================

        try:
            robot = Bot.get_instance(bot_id)

            if robot:
                await robot.stop()

        except Exception as e:
            LOGGER("Expiry").error(
                f"[EXPIRED STOP ERROR] {bot_id}: {e}"
            )

        # ==========================
        # UPDATE STATUS
        # ==========================

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
# CHECK REMINDER 3 DAYS
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

        remaining = expires_at - now

        if not (
            remaining <= timedelta(days=3)
            and remaining > timedelta(0)
            and not bot.get(
                "expiry_reminder",
                False
            )
        ):
            continue

        # ==========================
        # OWNER DARI DATABASE INDUK
        # ==========================

        owner = ownerdb.find_one({
            "bot_id": bot_id
        })

        if not owner:
            continue

        owner_id = owner.get("user_id")
        mention = (await app.get_users(owner_id)).mention
        
        if not owner_id:
            continue

        expires_text = (
            expires_at
            .astimezone(
                ZoneInfo("Asia/Jakarta")
            )
            .strftime(
                "%d-%m-%Y %H:%M:%S WIB"
            )
        )

        for bot in botdb.find({
            "grace_until": {
                "$exists": True
            }
        }):
        grace_until = bot.get("grace_until")
        
        if not grace_until:
            continue
            
        if grace_until.tzinfo is None:
            grace_until = grace_until.replace(
                tzinfo=timezone.utc
            )
            
        terminate_text = grace_until.astimezone(
            ZoneInfo("Asia/Jakarta")
        ).strftime(
            "%d-%m-%Y %H:%M:%S WIB"
        )

        text = (
            f"<b><u>Hai, {mention} 👋</u></b>\n\n"
            f"__Kami ingin mengingatkan bahwa bot yang anda sewa saat ini dalam jatuh tempo. Mohon segera lakukan perpanjangan agar bot tidak dihentikan.__\n\n"
            f"<b><u>🤖 Details Penting:</u></b>\n"
            f"<b><u>• ID |</u> `{bot_id}`</b>\n"
            f"<b><u>• Expired |</u> {expires_text}}</b>\n"
            f"<b><u>• Terminate |</u> {terminate_text}\n\n"
            "🛑 Jika pembayaran tidak dilakukan sebelum jatuh tempo, bot anda akan dihentikan sementara.\n"
            "⛔ Dan jika lewat dari tanggal terminate, data anda berisiko dihapus secara permanen.\n\n"
            "💳 Segera lakukan pembayaran untuk memastikan bot anda tetap aktif dan data anda masih aman.\n\n"
            "<b>Terimakasih Atas Kerjasamanya, Team SharingX 🙌</b>"
        )

        # ==========================
        # NOTIFIKASI DARI APP
        # ==========================

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

        # ==========================
        # NOTIFIKASI DARI BOT USER
        # ==========================

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

        # ==========================
        # REMINDER SUDAH DIKIRIM
        # ==========================

        await set_expiry_reminder(
            bot_id,
            True
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

    # ==========================
    # OWNER DATABASE INDUK
    # ==========================

    owner = ownerdb.find_one({
        "bot_id": bot_id
    })

    if not owner:
        return False

    owner_id = owner.get("user_id")

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
        "<b>🔴 Bot Anda Telah Expired</b>\n\n"
        f"<b>🤖 Bot ID:</b> "
        f"<code>{bot_id}</code>\n"
        f"<b>📅 Expired:</b> "
        f"<code>{expires_text}</code>\n\n"
        "<b>⚠️ Bot telah dihentikan sementara.</b>\n\n"
        "<b>⏳ Masa perpanjangan:</b> 3 hari\n"
        f"<b>📅 Batas akhir:</b> "
        f"<code>{grace_text}</code>\n\n"
        "Silakan lakukan perpanjangan sebelum "
        "batas waktu berakhir.\n\n"
        "Jika tidak diperpanjang, bot akan "
        "<b>dihapus secara permanen</b>."
    )

    # ==========================
    # NOTIFIKASI DARI APP
    # ==========================

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

    # ==========================
    # NOTIFIKASI DARI BOT
    # ==========================

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
                "expiry_reminder": False
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

        # ==========================
        # OWNER INDUK
        # ==========================

        owner = ownerdb.find_one({
            "bot_id": bot_id
        })

        owner_id = (
            owner.get("user_id")
            if owner
            else None
        )

        # ==========================
        # STOP BOT
        # ==========================

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

        # ==========================
        # TERMINATE NOTIFICATION
        # ==========================

        if owner_id:

            text = (
                "<b>⛔ Bot Telah Terminate</b>\n\n"
                f"<b>🤖 Bot ID:</b> "
                f"<code>{bot_id}</code>\n\n"
                "Masa perpanjangan selama "
                "<b>3 hari</b> telah berakhir.\n\n"
                "Data bot telah dihapus secara permanen "
                "dari database induk.\n\n"
                "Jika ingin menggunakan bot kembali, "
                "silakan membeli <b>Space Bot</b> baru "
                "dan membuat bot kembali."
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
