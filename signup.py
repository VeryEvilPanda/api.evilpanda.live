from random import getrandbits
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

async def generate_token():
    """
    Generates a random and unused token

    Returns:
        str: The token
    """
    token = '%0x' % getrandbits(30 * 4)
    users = await get_users()
    for user in users:
        if token == user.split('/')[2]:
            return await generate_token()
    else:
        return token


async def valid_email(email):
    """
    Checks if an email is already in the mailing list and if it's valid

    Args:
        email (str): The email to check

    Returns:
    string: Informationm about the validity
    """
    if '@' in email:
        users = await get_users()
        for user in users:
            if email == user.split('/')[1].strip():
                return 'exists'
        return 'added'
    else:
        return 'invalid'


async def add_user(email, name):
    """
    Adds a user to the mailing list

    Args:
        email (str): The email to add
        name (str): The name of the user
        
    Returns:
        str: Whether it was added (and why not)
    """
    result = await valid_email(email)
    if result == 'added':
        token = await generate_token()
        async with aiofiles.open('mailing_list.txt', 'a') as f:
            await f.write(f"{name}/{email}/{token}\n")
        return result
    else:
        return result
