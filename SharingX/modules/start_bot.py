from pyrogram import filters
from datetime import datetime

from SharingX import Bot


@Bot.on_message(filters.command("testdb") & filters.private)
async def test_database(client, message):

    try:
        db = client.db

        if db is None:
            return await message.reply_text(
                "<b>❌ Database bot belum terhubung.</b>"
            )


        collection = db["test_database"]


        data = {
            "user_id": message.from_user.id,
            "name": message.from_user.first_name,
            "time": datetime.now()
        }


        result = collection.insert_one(data)


        total = collection.count_documents({})


        await message.reply_text(
            f"<b>✅ Berhasil Menyimpan Data</b>\n\n"
            f"<b>Database:</b> <code>{db.name}</code>\n"
            f"<b>Collection:</b> <code>test_database</code>\n"
            f"<b>ID:</b> <code>{result.inserted_id}</code>\n"
            f"<b>Total Data:</b> {total}"
        )


    except Exception as e:

        await message.reply_text(
            f"<b>❌ Error:</b>\n<code>{e}</code>"
        )
