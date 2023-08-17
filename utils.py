import datetime
import calendar
import fastenv
from datetime import datetime, timezone, date
from random import getrandbits

async def date_to_timestamp(date):
    """
    Converts a date to a timestamp

    Args:
        date (date): The date to convert

    Returns:
        int: The timestamp
    """
    timestamp1 = calendar.timegm(date.timetuple())
    timestamp2 = datetime.utcfromtimestamp(timestamp1)
    return int(timestamp2.timestamp())


async def get_env_value(key):
    """
    Returns a specific value from the .env file

    Args:
        key (str): The key to the value

    Returns:
        str: The value
    """
    dotenv = await fastenv.load_dotenv('.env')
    if key in dotenv:
        return dotenv[key]
    else:
        raise Exception(f"Key {key} not found in .env file")


async def set_env_value(key, value):
    """
    Sets a specific value in the .env file

    Args:
        key (str): The key to the value
        value (str): The value to be set
    """
    dotenv = await fastenv.load_dotenv('.env')
    eval(f"dotenv.setenv({key}='{value}')")
    await fastenv.dump_dotenv(dotenv, ".env")

async def generate_hex_value():
    """
    Generates a random 30 character hex value

    Returns:
        str: The hex value
    """
    token = '%0x' % getrandbits(30 * 4)
    return str(token)