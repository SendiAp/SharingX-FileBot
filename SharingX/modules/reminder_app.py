import asyncio
from zoneinfo import ZoneInfo
from datetime import datetime, timedelta, timezone

from SharingX import app
from SharingX.helper.database import botdb, ownerdb

async def expiry_reminder_loop():
    while True:
        try:
            await check_expiry_reminder()
            await check_expired_bots()
            await check_terminate_bots()

        except Exception as e:
            print(
                f"[EXPIRY LOOP ERROR] {e}"
            )

        await asyncio.sleep(60)

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

        try:
            robot = Bot.get_instance(bot_id)

            if robot:
                await robot.stop()

        except Exception as e:
            print(
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

await notify_bot_expired(
    bot_id
)
        
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

        if (
            remaining <= timedelta(days=3)
            and remaining > timedelta(0)
            and not bot.get("expiry_reminder", False)
        ):
            owner = ownerdb.find_one({
                "bot_id": bot_id
            })

            if not owner:
                continue

            owner_id = owner.get("user_id")

            if not owner_id:
                continue

            try:
                await app.send_message(
                    owner_id,
                    "<b>⚠️ Peringatan Masa Aktif Bot</b>\n\n"
                    f"<b>🤖 Bot ID:</b> <code>{bot_id}</code>\n"
                    "<b>⏳ Masa aktif bot Anda akan berakhir dalam 3 hari.</b>\n\n"
                    f"<b>📅 Expired:</b> "
                    f"<code>{expires_at.astimezone(ZoneInfo('Asia/Jakarta')).strftime('%d-%m-%Y %H:%M:%S WIB')}</code>\n\n"
                    "Silakan lakukan perpanjangan sebelum masa aktif berakhir "
                    "agar bot tetap dapat digunakan."
                )

                await set_expiry_reminder(
                    bot_id,
                    True
                )

            except Exception as e:
                print(
                    f"[EXPIRY REMINDER ERROR] {bot_id}: {e}"
                )

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
        .astimezone(ZoneInfo("Asia/Jakarta"))
        .strftime("%d-%m-%Y %H:%M:%S WIB")
        if expires_at
        else "-"
    )

    grace_text = (
        grace_until
        .astimezone(ZoneInfo("Asia/Jakarta"))
        .strftime("%d-%m-%Y %H:%M:%S WIB")
        if grace_until
        else "-"
    )

    try:
        await app.send_message(
            owner_id,
            "<b>🔴 Bot Anda Telah Expired</b>\n\n"
            f"<b>🤖 Bot ID:</b> <code>{bot_id}</code>\n"
            f"<b>📅 Expired:</b> <code>{expires_text}</code>\n\n"
            "<b>⚠️ Bot telah dihentikan sementara.</b>\n\n"
            "<b>⏳ Masa perpanjangan:</b> 3 hari\n"
            f"<b>📅 Batas akhir:</b> <code>{grace_text}</code>\n\n"
            "Silakan lakukan perpanjangan sebelum batas waktu berakhir.\n\n"
            "Jika tidak diperpanjang, bot akan "
            "<b>dihapus secara permanen</b>."
        )

        return True

    except Exception as e:
        print(
            f"[EXPIRED NOTIFY ERROR] {bot_id}: {e}"
        )

        return False

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
        .astimezone(ZoneInfo("Asia/Jakarta"))
        .strftime("%d-%m-%Y %H:%M:%S WIB")
        if expires_at
        else "-"
    )

    grace_text = (
        grace_until
        .astimezone(ZoneInfo("Asia/Jakarta"))
        .strftime("%d-%m-%Y %H:%M:%S WIB")
        if grace_until
        else "-"
    )

    try:
        await app.send_message(
            owner_id,
            "<b>🔴 Bot Anda Telah Expired</b>\n\n"
            f"<b>🤖 Bot ID:</b> <code>{bot_id}</code>\n"
            f"<b>📅 Expired:</b> <code>{expires_text}</code>\n\n"
            "<b>⚠️ Bot telah dihentikan sementara.</b>\n\n"
            "<b>⏳ Masa perpanjangan:</b> 3 hari\n"
            f"<b>📅 Batas akhir:</b> <code>{grace_text}</code>\n\n"
            "Silakan lakukan perpanjangan sebelum batas waktu berakhir.\n\n"
            "Jika tidak diperpanjang, bot akan "
            "<b>dihapus secara permanen</b>."
        )

        return True

    except Exception as e:
        print(
            f"[EXPIRED NOTIFY ERROR] {bot_id}: {e}"
        )

        return False

async def renew_bot(bot_id, days=30):
    bot_id = str(bot_id)

    now = datetime.now(timezone.utc)

    bot = botdb.find_one({
        "bot_id": bot_id
    })

    if not bot:
        return False

    if bot.get("status") not in ["running", "expired"]:
        return False

    expires_at = bot.get("expires_at")

    if expires_at and expires_at.tzinfo is None:
        expires_at = expires_at.replace(
            tzinfo=timezone.utc
        )

    if expires_at and expires_at > now:
        new_expires_at = expires_at + timedelta(
            days=days
        )
    else:
        new_expires_at = now + timedelta(
            days=days
        )

    new_grace_until = new_expires_at + timedelta(
        days=3
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
        print(
            f"[RENEW BOT START ERROR] {bot_id}: {e}"
        )

        return False

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
        grace_until = bot.get("grace_until")

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

        try:
            robot = Bot.get_instance(bot_id)

            if robot:
                try:
                    await robot.stop()
                except Exception:
                    pass

        except Exception:
            pass

        if owner_id:
            try:
                await app.send_message(
                    owner_id,
                    "<b>⛔ Bot Telah Terminate</b>\n\n"
                    f"<b>🤖 Bot ID:</b> <code>{bot_id}</code>\n\n"
                    "Masa perpanjangan selama <b>3 hari</b> "
                    "telah berakhir.\n\n"
                    "Data bot telah dihapus secara permanen "
                    "dari database.\n\n"
                    "Jika ingin menggunakan bot kembali, "
                    "silakan membeli <b>Space Bot</b> baru "
                    "dan membuat bot kembali."
                )
            except Exception as e:
                print(
                    f"[TERMINATE NOTIFY ERROR] {bot_id}: {e}"
                )

        ownerdb.delete_one({
            "bot_id": bot_id
        })

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

        botdb.delete_one({
            "bot_id": bot_id
        })

