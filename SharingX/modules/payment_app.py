from pyrogram import filters
from pyrogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from Sharingx import app

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

    quantity = max(1, min(quantity, MAX_SPACE_BUY))

    await set_space_order(
        user_id,
        quantity=quantity
    )

    total = SPACE_PRICE * quantity

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
                f"❌ Maksimal pembelian {MAX_SPACE_BUY} Space.",
                show_alert=True
            )

        await space_buy_page(
            callback_query,
            quantity=quantity
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
# CLAIM VOUCHER
# =========================

@app.on_callback_query(
    filters.regex("^space_voucher$")
)
async def space_voucher(client, callback_query):
    await callback_query.answer(
        "🎟️ Fitur voucher belum tersedia.",
        show_alert=True
    )


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
