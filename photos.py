import aiofiles
import json
from datetime import datetime, timezone, date
import aiohttp
from utils import date_to_timestamp, get_env_value
import blurhash
from PIL.Image import fromarray as image_from_array
from numpy import array as numpy_array
from base64 import b64encode
from io import BytesIO
import asyncio

async def get_last_photo():
    """
    Returns the last photo information from the photos.json file

    Returns:
        date: The date of the last photo
        str: The url of the last photo
        str: The blurhash of the last photo
        str: The description of the last photo
        dict: The author of the last photo (name, url)
    """
    async with aiofiles.open('photos.json', 'r') as f:
        data = json.loads(await f.read())
        last_date = date.fromtimestamp(data['timestamp'])
        url = data['url']
        blurhash = data['blurhash']
        description = data['description']
        author = data['author']
    return last_date, url, blurhash, description, author


async def get_last_date():
    """
    Returns the last date from the photos.json file (faster if you only need the date)
    
    Returns:
        date: The date of the last photo
    """
    async with aiofiles.open('photos.json', 'r') as f:
        data = json.loads(await f.read())
        last_date = date.fromtimestamp(data['timestamp'])
    return last_date


async def blurhash_to_image(blurhash_value):
    """
    Converts a blurhash to a PIL image
    
    Args:
        blurhash_value (str): The blurhash to convert

    Returns:
        PIL.Image.Image: The base64 image
    """
    img = image_from_array(numpy_array(blurhash.decode(blurhash_value, 160, 90)).astype('uint8'))
    return img

async def image_to_base64(img):
    """
    Converts the PIL image to a base64 image
    
    Args:
        img (PIL.Image.Image): The blurhash to convert

    Returns:
        str: The image encoded in base64
    """
    buffered = BytesIO()
    img.save(buffered, format="JPEG")
    img_str = b64encode(buffered.getvalue())
    return img_str

async def get_new_photo():
    """
    Retrieves a new photo from Unsplash and updates the photos.json file
    
    Returns:
        date: The date of the new photo
        str: The url of the new photo
        str: The blurhash of the new photo
        str: The description of the new photo
        dict: The author of the new photo (name, url)
    """
    api_key = await get_env_value('UNSPLASH_API_KEY')
    async with aiohttp.request('GET', f'https://api.unsplash.com/photos/random?collections=1263731&orientation=landscape&client_id={api_key}') as response:
        data = await response.json()
        url = data['urls']['full']
        blurhash = data['blur_hash']
        description = data['description']
        author = {
            'name': data['user']['name'],
            'url': data['user']['links']['html']
        }
        today_date = date.today()
    async with aiofiles.open('photos.json', 'w') as f:
        data = {
            'timestamp': await date_to_timestamp(today_date),
            'url': url,
            'blurhash': blurhash,
            'description': description,
            'author': author
        }
        await f.write(json.dumps(data, ensure_ascii=False, indent=4))
    return today_date, url, blurhash, description, author



async def go():
    image = await blurhash_to_image("L69HFWjF4oxt*0M{oLxZ9vWBnNs.")
    base64_image = await image_to_base64(image)
    return base64_image
