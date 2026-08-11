import asyncio
from zoneinfo import ZoneInfo

from SharingX.helper.database import botdb

async def expiry_reminder_loop():
    while True:
        try:
            await check_expiry_reminder()
        except Exception as e:
            print(f"[EXPIRY LOOP ERROR] {e}")

        await asyncio.sleep(60)
      
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
