import os
import sys
import random
import asyncio

from datetime import datetime, timezone, timedelta
from pytz import timezone as pytz_timezone
from motor.motor_asyncio import AsyncIOMotorClient

from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from SharingX import app, Bot, LOGGER

from SharingX.helper.database import (
    renew_orderdb,
    get_renew_order,
    del_renew_order,
    renew_bot,
    get_bot_data,
    set_bot_status
)

from SharingX.helper.casaku import (
    generate_qris,
    check_payment_status
)

from SharingX.helper.qris import create_qris

from .renew1_app import format_rupiah


@app.on_callback_query(
    filters.regex(r"^renewpay_(.+)$")
)
async def renew_payment(client, callback_query):

    bot_id = callback_query.data.split(
        "renewpay_",
        1
    )[1]

    user_id = callback_query.from_user.id

    order = await get_renew_order(
        user_id,
        bot_id
    )

    if not order:
        return await callback_query.answer(
            "❌ Pesanan tidak ditemukan.",
            show_alert=True
        )

    total = int(
        order.get(
            "total",
            0
        )
    )

    if total < 1:
        return await callback_query.answer(
            "❌ Total pembayaran tidak valid.",
            show_alert=True
        )

    try:

        unique_fee = random.randint(
            1,
            1000
        )

        payment_amount = (
            total + unique_fee
        )

        res = await generate_qris(
            payment_amount
        )

        if not res or not res.get("data"):
            return await callback_query.answer(
                "❌ Gagal membuat QRIS.",
                show_alert=True
            )

        payment = res["data"]

        transaction_id = payment.get(
            "transactionId"
        )

        qris_string = payment.get(
            "qr_string"
        )

        total_payment = payment.get(
            "totalAmount",
            payment_amount
        )

        expired_time = payment.get(
            "expiredInMinutes",
            15
        )

        if not transaction_id:
            return await callback_query.answer(
                "❌ Transaction ID tidak ditemukan.",
                show_alert=True
            )

        if not qris_string:
            return await callback_query.answer(
                "❌ QRIS tidak ditemukan.",
                show_alert=True
            )

        qr_image = await create_qris(
            qris_string,
            int(total_payment)
        )

        payment_ref = (
            f"RNW"
            f"{user_id}"
            f"{int(datetime.now().timestamp())}"
        )

        wib = pytz_timezone(
            "Asia/Jakarta"
        )

        expires_at = (
            datetime.now(wib)
            + timedelta(
                minutes=int(expired_time)
            )
        )

        renew_orderdb.update_one(
            {
                "user_id": user_id,
                "bot_id": str(bot_id)
            },
            {
                "$set": {
                    "payment_ref": payment_ref,
                    "transaction_id": transaction_id,
                    "payment_status": "pending",
                    "payment_amount": int(total_payment),
                    "payment_expires_at": expires_at
                }
            }
        )

        await callback_query.message.delete()

        caption = (
            "<b>╭┄┄┄ PEMBAYARAN RENEW ┄┄┄╮</b>\n"
            f"<b>┆ 🤖 Bot ID</b>\n"
            f"<b>┆ ╰┈➤ <code>{bot_id}</code></b>\n"
            f"<b>┆ ⏰ Durasi</b>\n"
            f"<b>┆ ╰┈➤ {order['days']} Hari</b>\n"
            f"<b>┆ 💰 Total</b>\n"
            f"<b>┆ ╰┈➤ {format_rupiah(int(total_payment))}</b>\n"
            f"<b>┆ 🧾 Invoice</b>\n"
            f"<b>┆ ╰┈➤ <code>{payment_ref}</code></b>\n"
            f"<b>┆ ⏳ Expired</b>\n"
            f"<b>┆ ╰┈➤ {expires_at.strftime('%H:%M:%S')} WIB</b>\n"
            "<b>╰┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╯</b>\n\n"
            "<b>Silakan scan QRIS di atas untuk melakukan pembayaran.</b>"
        )

        qris_message = await app.send_photo(
            user_id,
            qr_image,
            caption=caption,
            reply_markup=InlineKeyboardMarkup([
                [
                    InlineKeyboardButton(
                        "❌ Batalkan",
                        callback_data=f"renewcancel_{bot_id}_{payment_ref}"
                    )
                ]
            ])
        )

        asyncio.create_task(
            check_renew_payment(
                user_id,
                bot_id,
                payment_ref,
                int(total_payment),
                qris_message,
                transaction_id,
                expires_at
            )
        )

    except Exception as e:

        LOGGER("Renew").error(
            f"[RENEW PAYMENT ERROR] {bot_id}: {e}"
        )

        await callback_query.answer(
            "❌ Terjadi kesalahan saat membuat pembayaran.",
            show_alert=True
        )


@app.on_callback_query(
    filters.regex(r"^renewcancel_(.+)_(RNW.+)$")
)
async def renew_cancel(client, callback_query):

    data = callback_query.data.split(
        "_",
        2
    )

    bot_id = data[1]
    payment_ref = data[2]

    user_id = callback_query.from_user.id

    renew_orderdb.update_one(
        {
            "user_id": user_id,
            "bot_id": str(bot_id),
            "payment_ref": payment_ref
        },
        {
            "$set": {
                "payment_status": "cancelled"
            }
        }
    )

    try:
        await callback_query.message.delete()
    except Exception:
        pass

    await app.send_message(
        user_id,
        "<b>──────〔 CANCEL 〕──────</b>\n\n"
        "Pembayaran perpanjangan dibatalkan.\n\n"
        f"<b>Invoice:</b> "
        f"<code>{payment_ref}</code>",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "💳 Buat Pembayaran Baru",
                    callback_data=f"renew_{bot_id}"
                )
            ]
        ])
    )


async def check_renew_payment(
    user_id,
    bot_id,
    payment_ref,
    amount,
    qris_message,
    transaction_id,
    expires_at
):

    while True:

        try:

            order = await get_renew_order(
                user_id,
                bot_id
            )

            if not order:
                return

            if order.get(
                "payment_status"
            ) != "pending":
                return

            wib = pytz_timezone(
                "Asia/Jakarta"
            )

            now = datetime.now(wib)

            if now >= expires_at:

                renew_orderdb.update_one(
                    {
                        "user_id": user_id,
                        "bot_id": str(bot_id),
                        "payment_ref": payment_ref
                    },
                    {
                        "$set": {
                            "payment_status": "expired"
                        }
                    }
                )

                try:
                    await qris_message.delete()
                except Exception:
                    pass

                await app.send_message(
                    user_id,
                    "<b>──────〔 EXPIRED 〕──────</b>\n\n"
                    "Pembayaran perpanjangan telah kadaluarsa.\n\n"
                    f"<b>Invoice:</b> "
                    f"<code>{payment_ref}</code>",
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton(
                                "💳 Buat Pembayaran Baru",
                                callback_data=f"renew_{bot_id}"
                            )
                        ]
                    ])
                )

                return

            res = await check_payment_status(
                transaction_id
            )

            data = res.get(
                "data",
                {}
            )

            status = data.get(
                "status"
            )

            if status == "expired":

                renew_orderdb.update_one(
                    {
                        "user_id": user_id,
                        "bot_id": str(bot_id),
                        "payment_ref": payment_ref
                    },
                    {
                        "$set": {
                            "payment_status": "expired"
                        }
                    }
                )

                try:
                    await qris_message.delete()
                except Exception:
                    pass

                await app.send_message(
                    user_id,
                    "<b>──────〔 EXPIRED 〕──────</b>\n\n"
                    "Pembayaran perpanjangan telah kadaluarsa.\n\n"
                    f"<b>Invoice:</b> "
                    f"<code>{payment_ref}</code>",
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton(
                                "💳 Buat Pembayaran Baru",
                                callback_data=f"renew_{bot_id}"
                            )
                        ]
                    ])
                )

                return

            if status == "paid":

                order = await get_renew_order(
                    user_id,
                    bot_id
                )

                if not order:
                    return

                success = await renew_bot(
                    bot_id,
                    days=int(
                        order["days"]
                    )
                )

                if not success:

                    LOGGER("Renew").error(
                        f"[RENEW FAILED] {bot_id}"
                    )

                    return

                renew_orderdb.update_one(
                    {
                        "user_id": user_id,
                        "bot_id": str(bot_id),
                        "payment_ref": payment_ref
                    },
                    {
                        "$set": {
                            "payment_status": "paid",
                            "paid_at": datetime.now(
                                timezone.utc
                            )
                        }
                    }
                )

                try:
                    await qris_message.delete()
                except Exception:
                    pass

                bot_started = False

                robot = Bot.get_instance(
                    str(bot_id)
                )

                if robot:

                    is_connected = getattr(
                        robot,
                        "is_connected",
                        False
                    )

                    if is_connected:

                        bot_started = True

                        LOGGER("Renew").info(
                            f"[RENEW] Bot {bot_id} masih aktif."
                        )

                    else:

                        try:

                            await robot.start()

                            bot_started = True

                            await set_bot_status(
                                bot_id,
                                "running"
                            )

                            LOGGER("Renew").info(
                                f"[RENEW] Bot {bot_id} berhasil "
                                f"dinyalakan kembali."
                            )

                        except Exception as e:

                            LOGGER("Renew").error(
                                f"[RENEW START ERROR] "
                                f"{bot_id}: {e}"
                            )

                else:

                    try:

                        bot_data = await get_bot_data(
                            bot_id
                        )

                        if not bot_data:
                            raise Exception(
                                "Data bot tidak ditemukan."
                            )

                        robot = Bot(
                            name=str(bot_id),
                            api_id=bot_data["api_id"],
                            api_hash=bot_data["api_hash"],
                            bot_token=bot_data["bot_token"]
                        )

                        robot.in_memory = False

                        mongo = AsyncIOMotorClient(
                            bot_data["mongo_url"]
                        )

                        robot.mongo = mongo

                        robot.db = mongo[
                            bot_data.get(
                                "database",
                                "sharingx"
                            )
                        ]

                        await robot.start()

                        bot_started = True

                        await set_bot_status(
                            bot_id,
                            "running"
                        )

                        LOGGER("Renew").info(
                            f"[RENEW] Bot {bot_id} berhasil "
                            f"dibuat ulang dan dinyalakan."
                        )

                        os.execv(
                            sys.executable,
                            [sys.executable, "-m", "SharingX"]
                        )
                    except Exception as e:

                        LOGGER("Renew").error(
                            f"[RENEW RESTART ERROR] "
                            f"{bot_id}: {e}"
                        )

                if not bot_started:

                    await set_bot_status(
                        bot_id,
                        "expired"
                    )

                    LOGGER("Renew").warning(
                        f"[RENEW] Bot {bot_id} berhasil "
                        f"diperpanjang tetapi gagal dinyalakan."
                    )

                await app.send_message(
                    user_id,
                    "<b>╭┄┄┄ PEMBAYARAN BERHASIL ┄┄┄╮</b>\n\n"
                    f"<b>🤖 Bot ID:</b> "
                    f"<code>{bot_id}</code>\n"
                    f"<b>⏰ Durasi:</b> "
                    f"{order['days']} Hari\n"
                    f"<b>💰 Pembayaran:</b> "
                    f"{format_rupiah(amount)}\n"
                    f"<b>🧾 Invoice:</b> "
                    f"<code>{payment_ref}</code>\n\n"
                    + (
                        "<b>✅ Bot berhasil diperpanjang dan "
                        "dinyalakan kembali.</b>\n"
                        if bot_started
                        else
                        "<b>⚠️ Bot berhasil diperpanjang, "
                        "tetapi gagal dinyalakan.</b>\n"
                    )
                    + (
                        "<b>Terimakasih telah menggunakan "
                        "layanan SharingX.</b>"
                    ),
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton(
                                "🤖 Lihat Bot",
                                callback_data=f"bot_{bot_id}"
                            )
                        ]
                    ])
                )

                await del_renew_order(
                    user_id,
                    bot_id
                )

                return

            await asyncio.sleep(20)

        except Exception as e:

            LOGGER("Renew").error(
                f"[RENEW CHECK ERROR] "
                f"{bot_id}: {e}"
            )

            await asyncio.sleep(20)
