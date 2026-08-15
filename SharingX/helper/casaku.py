import aiohttp

from SharingX.helper.database import get_renew_casaku


CASAKU_BASE_URL = "https://api.casaku.id/api/generate"


async def generate_qris(amount):
    req = await get_renew_casaku()

    if not req:
        return None

    url = f"{CASAKU_BASE_URL}/v2/qris"

    payload = {
        "qr_id": req.get("qr_id"),
        "amount": amount,
        "useUniqueCode": True,
        "packageIds": [
            "id.dana",
            "com.gojek.gopaymerchant"
        ],
        "expiredInMinutes": 15,
        "qrType": "dynamic",
        "paymentMethod": "qris",
        "useQris": True
    }

    headers = {
        "x-license-key": req.get("license"),
        "content-type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json=payload,
            headers=headers
        ) as response:

            try:
                return await response.json()

            except Exception:
                return {
                    "status": response.status,
                    "error": await response.text()
                }


async def check_payment_status(transaction_id):
    req = await get_renew_casaku()

    if not req:
        return None

    url = f"{CASAKU_BASE_URL}/check-status"

    payload = {
        "transactionId": transaction_id
    }

    headers = {
        "x-license-key": req.get("license"),
        "content-type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json=payload,
            headers=headers
        ) as response:

            try:
                return await response.json()

            except Exception:
                return {
                    "status": response.status,
                    "error": await response.text()
                }


async def cancel_payment_status(transaction_id):
    req = await get_renew_casaku()

    if not req:
        return None

    url = f"{CASAKU_BASE_URL}/cancel-status"

    payload = {
        "transactionId": transaction_id
    }

    headers = {
        "x-license-key": req.get("license"),
        "content-type": "application/json"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(
            url,
            json=payload,
            headers=headers
        ) as response:

            try:
                return await response.json()

            except Exception:
                return {
                    "status": response.status,
                    "error": await response.text()
                }
