async def remove_duplicates(users):
    seen = set()
    unique_users = []
    
    for user in users:
        if user not in seen:
            seen.add(user)
            unique_users.append(user)
        else:
            await del_user(user)
    return unique_users
  
@bot.on_message(filters.command(["broadcast", "gcast"]) & filters.private & filters.user(OWNER_ID))
async def broadcast(client, message):
    if not message.reply_to_message:
        return await message.reply("🔄 __Silahkan balas ke pesan__", quote=True)

    users = await get_user()
    if not users:
        return await message.reply("🚫 Tidak ada pengguna yang terdaftar untuk menerima broadcast.", quote=True)

    users = await remove_duplicates(users)
    broadcast_msg = message.reply_to_message
    total, successful, blocked, deleted, unsuccessful = 0, 0, 0, 0, 0

    pls_wait = await message.reply("📡 ʙʀᴏᴀᴅᴄᴀsᴛɪɴɢ ᴍᴇssᴀɢᴇ, sɪʟᴀʜᴋᴀɴ ᴛᴜɴɢɢᴜ sᴇʙᴇɴᴛᴀʀ", quote=True)
            
        total += 1
        try:
          await broadcast_msg.copy(user_id)
            successful += 1
        except FloodWait as e:
            await asyncio.sleep(e.x)

            if not broadcast:
                await broadcast_msg.forward(user_id)
            else:
                await broadcast_msg.copy(user_id)
                
            successful += 1
        except UserIsBlocked:
            await del_user(user_id)
            blocked += 1
        except InputUserDeactivated:
            await del_user(user_id)
            deleted += 1
        except Exception:
            await del_user(user_id)
            unsuccessful += 1

    status = (
        "<u>✅ ʙʀᴏᴀᴅᴄᴀsᴛ sᴜᴄᴄᴇss</u>\n"
        f"👥 ᴛᴏᴛᴀʟ ᴜsᴇʀs: <code>{total}</code>\n"
        f"📩 ᴛᴇʀᴋɪʀɪᴍ: <code>{successful}</code>\n"
        f"❌ ᴛɪᴅᴀᴋ ᴛᴇʀᴋɪʀɪᴍ: <code>{unsuccessful}</code>\n"
        f"🚫 ʙʟᴏᴄᴋ ᴘᴇɴɢɢᴜɴᴀ: <code>{blocked}</code>\n"
        f"🗑️ ᴀᴋᴜɴ ᴛᴇʀʜᴀᴘᴜs: <code>{deleted}</code>"
    )

    await pls_wait.edit(status)
