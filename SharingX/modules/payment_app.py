from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from SharingX import app
from SharingX.helper.database import set_space_order, get_space_order

SPACE_PRICE = 45000
MAX_SPACE_BUY = 50

def format_rupiah(amount):
    return f"Rp{amount:,}".replace(",", ".")

# =========================
# BUY SPACE
# =========================

@app.on_callback_query(filters.regex("^buy_space$"))
async def buy_space(client, callback_query):
    await space_buy_page(
        callback_query,
        quantity=1
    )

async def space_buy_page(callback_query, quantity=1):
    user_id = callback_query.from_user.id

    quantity = max(
        1,
        min(quantity, MAX_SPACE_BUY)
    )

    old_order = await get_space_order(user_id)

    voucher_used = None
    discount = 0

    if old_order:
        voucher_used = old_order.get("voucher_used")
        discount = int(old_order.get("discount", 0))

    if voucher_used:
        voucher = discount_collection.find_one({
            "code": voucher_used
        })

        if not voucher or not voucher.get("active", True):
            voucher_used = None
            discount = 0

    total = max(
        0,
        (SPACE_PRICE * quantity) - discount
    )

    await set_space_order(
        user_id=user_id,
        quantity=quantity,
        price=SPACE_PRICE,
        voucher=voucher_used,
        discount=discount
    )

    buttons = [
        [
            InlineKeyboardButton(
                "➖",
                callback_data=f"space_qty_{quantity - 1}"
            ),
            InlineKeyboardButton(
                str(quantity),
                callback_data="space_noop"
            ),
            InlineKeyboardButton(
                "➕",
                callback_data=f"space_qty_{quantity + 1}"
            )
        ],
        [
            InlineKeyboardButton(
                "🎟️ Claim Kode Voucher",
                callback_data="space_voucher"
            )
        ],
        [
            InlineKeyboardButton(
                "💳 Lanjutkan Pembayaran",
                callback_data="space_payment"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Kembali",
                callback_data="back_start"
            )
        ]
    ]

    if voucher_used:
        text = (
            "<b>╭┄┄┄ RINCIAN PESANAN ┄┄┄╮</b>\n"
            "<b>┆ 📦 Harga</b>\n"
            f"<b>┆  ╰┈➤ {format_rupiah(SPACE_PRICE)}/space</b>\n"
            "<b>┆ ┄┄┄┄┄┄┄┄┄┄</b>\n"
            "<b>┆ 🔢 Jumlah Beli</b>\n"
            f"<b>┆ ╰┈➤ {quantity} space</b>\n"
            "<b>┆ 🎟️ Voucher</b>\n"
            f"<b>┆ ╰┈➤ <code>{voucher_used}</code></b>\n"
            "<b>┆ 💸 Potongan Harga</b>\n"
            f"<b>┆ ╰┈➤ {format_rupiah(discount)}</b>\n"
            "<b>┆ ┄┄┄┄┄┄┄┄┄┄</b>\n"
            "<b>┆ ✅ Total Pembayaran</b>\n"
            f"<b>┆ ╰┈➤ {format_rupiah(total)}</b>\n"
            "<b>╰┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╯</b>\n\n"
            "<b>Kalau Sudah Selesai Semua Bisa 💳 "
            "Lanjutkan Pembayaran Ya:</b>"
        )

    else:
        text = (
            "<b>╭┄┄┄ RINCIAN PESANAN ┄┄┄╮</b>\n"
            "<b>┆ 📦 Harga</b>\n"
            f"<b>┆  ╰┈➤ {format_rupiah(SPACE_PRICE)}/space</b>\n"
            "<b>┆ ┄┄┄┄┄┄┄┄┄┄</b>\n"
            "<b>┆ 🔢 Jumlah Beli</b>\n"
            f"<b>┆ ╰┈➤ {quantity} space</b>\n"
            "<b>┆ ✅ Total Pembayaran</b>\n"
            f"<b>┆ ╰┈➤ {format_rupiah(total)}</b>\n"
            "<b>╰┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄┄╯</b>\n\n"
            "<b>Kalau Sudah Selesai Semua Bisa 💳 "
            "Lanjutkan Pembayaran Ya:</b>"
        )

    await callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
    )

# =========================
# JUMLAH SPACE
# =========================
@app.on_callback_query(
    filters.regex(r"^space_qty_(\d+)$")
)
async def space_quantity(client, callback_query):
    try:
        quantity = int(
            callback_query.data.split("_")[-1]
        )

        if quantity < 1:
            return await callback_query.answer(
                "❌ Minimal pembelian 1 Space.",
                show_alert=True
            )

        if quantity > MAX_SPACE_BUY:
            return await callback_query.answer(
                f"❌ Maksimal {MAX_SPACE_BUY} Space.",
                show_alert=True
            )

        await space_buy_page(
            callback_query,
            quantity
        )

    except Exception:
        await callback_query.answer(
            "❌ Terjadi kesalahan.",
            show_alert=True
        )

# =========================
# BUTTON JUMLAH
# =========================

@app.on_callback_query(
    filters.regex("^space_noop$")
)
async def space_noop(client, callback_query):
    await callback_query.answer()

# =========================
# LANJUTKAN PEMBAYARAN
# =========================

@app.on_callback_query(
    filters.regex("^space_payment$")
)
async def space_payment(client, callback_query):
    user_id = callback_query.from_user.id

    order = await get_space_order(user_id)

    if not order:
        return await callback_query.answer(
            "❌ Pesanan tidak ditemukan.",
            show_alert=True
        )

    quantity = order.get("quantity", 1)
    total = order.get(
        "total",
        SPACE_PRICE * quantity
    )

    text = (
        "<b>╭┄┄┄ KONFIRMASI PEMBAYARAN ┄┄┄╮</b>\n"
        f"<b>┆ 📦 Space</b>\n"
        f"<b>┆ ╰┈➤ {quantity} space</b>\n"
        f"<b>┆ 💰 Total</b>\n"
        f"<b>┆ ╰┈➤ {format_rupiah(total)}</b>\n"
        "<b>╰┄┄┄┄┄┄┄┄┄┄┄┄┄┄╯</b>\n\n"
        "<b>💳 Silakan lanjutkan pembayaran "
        "untuk mendapatkan Space Bot.</b>"
    )

    buttons = [
        [
            InlineKeyboardButton(
                "💳 Bayar Sekarang",
                callback_data="pay_space"
            )
        ],
        [
            InlineKeyboardButton(
                "🔙 Kembali",
                callback_data="buy_space"
            )
        ]
    ]

    await callback_query.edit_message_text(
        text,
        reply_markup=InlineKeyboardMarkup(buttons)
  )

# =========================
# CLAIM VOUCHER
# =========================

@app.on_callback_query(
    filters.regex("^space_voucher$")
)
async def space_voucher(client, callback_query):
    user_id = callback_query.from_user.id

    order = await get_space_order(user_id)

    if not order:
        return await callback_query.answer(
            "❌ Pesanan tidak ditemukan.",
            show_alert=True
        )

    old_voucher = order.get("voucher_used")

    if old_voucher:
        return await callback_query.answer(
            f"⚠️ Voucher {old_voucher} sudah digunakan.",
            show_alert=True
        )

    callback = await callback_query.edit_message_text(
        "<b>🎟️ Silakan Masukan Kode Voucher?</b>\n\n"
        "<i>Ketik /cancel untuk membatalkan.</i>"
    )

    while True:
        try:
            new_voucher_message = await client.listen(
                user_id
            )

            if not new_voucher_message.text:
                await new_voucher_message.delete()
                continue

            if new_voucher_message.text.startswith("/"):
                await new_voucher_message.delete()

                return await callback.edit(
                    "<b>❌ Proses Input Voucher Dibatalkan!</b>",
                    reply_markup=InlineKeyboardMarkup([
                        [
                            InlineKeyboardButton(
                                "🔙 Kembali",
                                callback_data="buy_space"
                            )
                        ]
                    ])
                )

            voucher_code = (
                new_voucher_message.text
                .strip()
                .upper()
            )

            voucher = discount_collection.find_one({
                "code": voucher_code
            })

            if not voucher or not voucher.get("active", True):
                await new_voucher_message.delete()

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
                voucher.get("discount", 0)
            )

            quantity = int(
                order.get("quantity", 1)
            )

            price = int(
                order.get("price", SPACE_PRICE)
            )

            total = max(
                0,
                (price * quantity) - discount
            )

            space_orderdb.update_one(
                {"user_id": user_id},
                {
                    "$set": {
                        "voucher_used": voucher_code,
                        "discount": discount,
                        "total": total
                    }
                }
            )

            await new_voucher_message.delete()

            return await space_buy_page(
                callback_query,
                quantity=quantity
            )

        except Exception as e:
            return await callback.edit(
                f"<b>❌ Terjadi Kesalahan:</b>\n"
                f"<code>{e}</code>"
        )
