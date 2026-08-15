import time
import random
import asyncio
import requests

from decimal import Decimal
from datetime import datetime, timedelta, timezone
from pytz import timezone as pytz_timezone

from pyrogram import filters
from pyrogram.types import (
    InlineKeyboardMarkup,
    InlineKeyboardButton
)

from SharingX import app, Bot, LOGGER

from SharingX.helper.database import (
    botdb,
    ownerdb,
    renew_orderdb,
    renew_voucherdb,
    renew_pricedb,
    get_bot_data,
    get_renew_order,
    set_renew_order,
    del_renew_order,
    get_renew_price,
    renew_bot,
    set_renew_payment
)

from SharingX.helper.qris import create_qris
from SharingX.helper.casaku import (
    generate_qris,
    check_payment_status,
    cancel_payment_status
)


def format_rupiah(amount):
    return f"Rp{int(amount):,}".replace(",", ".")


RENEW_PLANS = {
    "weekly": {
        "name": "Weekly",
        "days": 7,
        "label": "7 Hari"
    },
    "monthly": {
        "name": "Monthly",
        "days": 30,
        "label": "30 Hari"
    },
    "semi": {
        "name": "Semi-Annually",
        "days": 180,
        "label": "180 Hari"
    }
}


@app.on_callback_query(
    filters.regex(r"^renew_(.+)$")
)
async def renew_menu(client, callback_query):

    bot_id = callback_query.data.split(
        "renew_",
        1
    )[1]

    bot_data = await get_bot_data(bot_id)

    if not bot_data:
        return await callback_query.answer(
            "⚠️ Bot Tidak Ditemukan!",
            show_alert=True
        )

    owner = ownerdb.find_one({
        "bot_id": str(bot_id)
    })

    if not owner:
        return await callback_query.answer(
            "❌ Pemilik Bot Tidak Ditemukan!",
            show_alert=True
        )

    if int(owner.get("user_id", 0)) != callback_query.from_user.id:
        return await callback_query.answer(
            "❌ Kamu bukan pemilik bot ini!",
            show_alert=True
        )

    await callback_query.edit_message_text(
        "<b><u>💳 PERPANJANG BOT</u></b>\n"
        "––––—––––———––•\n\n"
        f"<b>🤖 Bot ID:</b> <code>{bot_id}</code>\n\n"
        "<b>Pilih durasi perpanjangan:</b>\n\n"
        "🗓 <b>Weekly</b>\n"
        "<i>7 Days</i>\n\n"
        "📅 <b>Monthly</b>\n"
        "<i>30 Days</i>\n\n"
        "📆 <b>Semi-Annually</b>\n"
        "<i>180 Days</i>",
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🗓 Weekly",
                    callback_data=f"renewplan_weekly_{bot_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "📅 Monthly",
                    callback_data=f"renewplan_monthly_{bot_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "📆 Semi-Annually",
                    callback_data=f"renewplan_semi_{bot_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Kembali",
                    callback_data=f"bot_{bot_id}"
                )
            ]
        ])
    )


@app.on_callback_query(
    filters.regex(r"^renewplan_(weekly|monthly|semi)_(.+)$")
)
async def renew_plan(client, callback_query):

    parts = callback_query.data.split("_", 2)

    plan = parts[1]
    bot_id = parts[2]

    if plan not in RENEW_PLANS:
        return await callback_query.answer(
            "❌ Paket tidak ditemukan.",
            show_alert=True
        )

    bot_data = await get_bot_data(bot_id)

    if not bot_data:
        return await callback_query.answer(
            "⚠️ Bot Tidak Ditemukan!",
            show_alert=True
        )

    owner = ownerdb.find_one({
        "bot_id": str(bot_id)
    })

    if not owner:
        return await callback_query.answer(
            "❌ Pemilik Bot Tidak Ditemukan!",
            show_alert=True
        )

    if int(owner.get("user_id", 0)) != callback_query.from_user.id:
        return await callback_query.answer(
            "❌ Kamu bukan pemilik bot ini!",
            show_alert=True
        )

    plan_data = RENEW_PLANS[plan]

    price = await get_renew_price(plan)

    if price is None:
        return await callback_query.answer(
            "❌ Harga paket belum tersedia.",
            show_alert=True
        )

    await set_renew_order(
        user_id=callback_query.from_user.id,
        bot_id=bot_id,
        plan=plan,
        days=plan_data["days"],
        price=price,
        voucher=None,
        discount=0
    )

    await renew_order_page(
        callback_query,
        bot_id
    )


async def renew_order_page(
    callback_query,
    bot_id
):

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

    plan = order.get("plan")

    plan_data = RENEW_PLANS.get(plan)

    if not plan_data:
        return await callback_query.answer(
            "❌ Paket tidak valid.",
            show_alert=True
        )

    price = int(
        order.get(
            "price",
            0
        )
    )

    discount = int(
        order.get(
            "discount",
            0
        )
    )

    voucher = order.get(
        "voucher_used"
    )

    total = max(
        0,
        price - discount
    )

    await set_renew_order(
        user_id=user_id,
        bot_id=bot_id,
        plan=plan,
        days=plan_data["days"],
        price=price,
        voucher=voucher,
        discount=discount
    )

    text = (
        "<b>╭┄┄┄ RINCIAN PERPANJANGAN ┄┄┄╮</b>\n"
        "<b>┆ 🤖 Bot ID</b>\n"
        f"<b>┆ ╰┈➤ <code>{bot_id}</code></b>\n"
        "<b>┆ ⏰ Durasi</b>\n"
        f"<b>┆ ╰┈➤ {plan_data['name']} "
        f"({plan_data['days']} Hari)</b>\n"
        "<b>┆ 📦 Harga</b>\n"
        f"<b>┆ ╰┈➤ {format_rupiah(price)}</b>\n"
    )

    if voucher:
        text += (
            "<b>┆ 🎟️ Voucher</b>\n"
            f"<b>┆ ╰┈➤ <code>{voucher}</code></b>\n"
            "<b>┆ 💸 Potongan Harga</b>\n"
            f"<b>┆ ╰┈➤ {format_rupiah(discount)}</b>\n"
        )

    text += (
        "<b>┆ ┄┄┄┄┄┄┄┄┄┄</b>\n"
        "<b>┆ 💰 Total Pembayaran</b>\n"
        f"<b>┆ ╰┈➤ {format_rupiah(total)}</b>\n"
        "<b>╰┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╯</b>\n\n"
        "<b>Silakan periksa kembali pesanan Anda.</b>"
    )

    await callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup([
            [
                InlineKeyboardButton(
                    "🎟️ Claim Code Voucher",
                    callback_data=f"renewvoucher_{bot_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "💳 Bayar Sekarang",
                    callback_data=f"renewpay_{bot_id}"
                )
            ],
            [
                InlineKeyboardButton(
                    "🔙 Kembali",
                    callback_data=f"renew_{bot_id}"
                )
            ]
        ])
    )


@app.on_callback_query(
    filters.regex(r"^renewvoucher_(.+)$")
)
async def renew_voucher(client, callback_query):

    bot_id = callback_query.data.split(
        "renewvoucher_",
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

    voucher_used = order.get(
        "voucher_used"
    )

    if voucher_used:
        return await callback_query.answer(
            f"⚠️ Voucher {voucher_used} sudah digunakan.",
            show_alert=True
        )

    message = await callback_query.edit_message_text(
        "<b>🎟️ Masukkan Code Voucher</b>\n\n"
        "<i>Ketik /cancel untuk membatalkan.</i>"
    )

    while True:

        try:

            voucher_message = await client.listen(
                user_id
            )

            if not voucher_message.text:

                try:
                    await voucher_message.delete()
                except Exception:
                    pass

                continue

            if voucher_message.text.startswith("/"):

                try:
                    await voucher_message.delete()
                except Exception:
                    pass

                return await message.edit(
                    "<b>❌ Proses Input Voucher Dibatalkan!</b>",
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton(
                                "🔙 Kembali",
                                callback_data=f"renew_{bot_id}"
                            )
                        ]
                    ])
                )

            code = (
                voucher_message.text
                .strip()
                .upper()
            )

            voucher = renew_voucherdb.find_one({
                "code": code,
                "active": True
            })

            if not voucher:

                try:
                    await voucher_message.delete()
                except Exception:
                    pass

                notice = await callback_query.message.reply_text(
                    "<b>❌ Voucher tidak valid atau sudah tidak aktif.</b>"
                )

                await asyncio.sleep(2)

                try:
                    await notice.delete()
                except Exception:
                    pass

                continue

            discount = int(
                voucher.get(
                    "discount",
                    0
                )
            )

            price = int(
                order.get(
                    "price",
                    0
                )
            )

            discount = min(
                discount,
                price
            )

            await set_renew_order(
                user_id=user_id,
                bot_id=bot_id,
                plan=order["plan"],
                days=order["days"],
                price=price,
                voucher=code,
                discount=discount
            )

            renew_voucherdb.update_one(
                {
                    "code": code
                },
                {
                    "$inc": {
                        "used": 1
                    }
                }
            )

            try:
                await voucher_message.delete()
            except Exception:
                pass

            return await renew_order_page(
                callback_query,
                bot_id
            )

        except Exception as e:

            return await message.edit(
                f"<b>❌ Terjadi Kesalahan:</b>\n"
                f"<code>{str(e)}</code>",
                reply_markup=InlineKeyboardMarkup([
                    [
                        InlineKeyboardButton(
                            "🔙 Kembali",
                            callback_data=f"renew_{bot_id}"
                        )
                    ]
                ])
        )
