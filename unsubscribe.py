import aiofiles

async def get_users():
    """
    Returns the users from the mailing_list.txt file

    Returns:
        list: The users
    """
    async with aiofiles.open('mailing_list.txt', 'r') as f:
        users = await f.readlines()
    return users


async def remove_user(email, token):
    """
    If user is in the mailing list, removes it

    Args:
        email (str): The email of the user
        token (str): The token of the user

    Returns:
        bool: If the user was removed
    """
    users = await get_users()
    new_users = users.copy()
    for user in users:
        user = user.split('/')
        if user[1].strip() == email and user[2].strip() == token:
            new_users.remove(f'{user[0]}/{user[1]}/{user[2]}')
            async with aiofiles.open('mailing_list.txt', 'w') as f:
                await f.writelines(new_users)
            return True
    return False
    