async def owner_admin_filter(_, client, message):
    user_id = message.from_user.id

    if await is_owner(client, user_id):
        return True

    if await is_admin(client, user_id):
        return True

    return False

owner_admin = filters.create(owner_admin_filter)
