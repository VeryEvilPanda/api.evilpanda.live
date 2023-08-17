from quart import Quart, render_template, websocket, abort, request, redirect
from datetime import date, timedelta
from photos import get_last_photo, get_last_date, get_new_photo
from unsubscribe import remove_user
from signup import add_user
from utils import get_env_value, set_env_value, generate_hex_value
from quart_rate_limiter import RateLimiter, rate_limit
from message import process_message
from dungeons import get_dungeons, get_dungeon_party

VALID_ERROR_CODES = ['400', '401', '403', '404', '405', '406', '407', '408', '409', '410', '411', '412', '413', '414', '415', '416', '417', '418', '421', '422', '423', '424', '425', '426', '428', '429', '431', '451', '500']

app = Quart(__name__)
rate_limiter = RateLimiter(app)

@app.route('/')
async def index():
    return await render_template('index.html')

@app.route('/mail/new_email', methods=['POST'])
async def new_email():
    form = await request.form
    email_dict = {
        'from': form['from'],
        'sender': form['sender'],
        'to': form['recipient'],
        'subject': form['subject'],
        'body': form['body-plain'],
        'timestamp': form['timestamp'],
        'attachments': form['attachment-count'],
        'token': form['token']
    }
    print(email_dict)
    return 'OK'

@app.route('/api')
async def main():
    if 'egg' in request.args:
        egg = request.args['egg'].strip()
        if egg.isnumeric() and egg in VALID_ERROR_CODES:
            print(f"Egg activated, code {egg}")
            abort(int(egg))
        else:
            return {'hello': 'world'}
    return {'hello': 'world'}

@app.route('/api/photos')
async def photos():
    last_date = await get_last_date()
    return {
        "contact": "https://discord.gg/Zu6pDEBCjY",
        "unsplash_status": "https://status.unsplash.com/",
        "daily": {
            "last_updated": last_date.strftime('%Y-%m-%d'),
            "url": "https://api.evilpanda.live/api/photos/daily"
        }
    }

@app.route('/api/photos/daily')
async def daily_photo():
    last_date = await get_last_date()
    force_password = await get_env_value('FORCE_PASSWORD')
    if 'force' in request.args and request.args['force'] == force_password:
        print("Forced update")
        await set_env_value('FORCE_PASSWORD', await generate_hex_value())
        today_date, url, blurhash, description, author = await get_new_photo()
        return {
            'forced': True,
            'date': today_date.strftime('%Y-%m-%d'),
            'url': url,
            'blurhash': blurhash,
            'description': description,
            'author': author
        }
    elif last_date != date.today():
        today_date, url, blurhash, description, author = await get_new_photo()
        return {
            'date': today_date.strftime('%Y-%m-%d'),
            'url': url,
            'blurhash': blurhash,
            'description': description,
            'author': author
        }
    else:
        last_date, url, blurhash, description, author = await get_last_photo()
        return {
            'date': last_date.strftime('%Y-%m-%d'),
            'url': url,
            'blurhash': blurhash,
            'description': description,
            'author': author
        }
        


@app.route('/briefing/unsubscribe')
async def unsubscribe():
    email = request.args['email'].strip()
    token = request.args['token'].strip()
    result = await remove_user(email, token)
    if result:
        return f'You have been unsubscribed from the BotPanda daily briefing service.\nEmail: {email}\nToken: {token}'  
    else:
        return 'An error occured. User does not exist. If you believe we are in error, join the support server at https://discord.gg/Zu6pDEBCjY'      


@app.route('/briefing/signup')
@rate_limit(2, timedelta(minutes=1))
@rate_limit(5, timedelta(hours=1))
@rate_limit(10, timedelta(days=1))
async def signup():
    email = request.args['email'].strip()
    name = request.args['name'].strip()
    result = await add_user(email, name)
    if result == 'added':
        return f'<!DOCTYPE html>You have been subscribed to the BotPanda daily briefing service.\nEmail: {email}\nName: {name}'
    elif result == 'exists':
        return '<!DOCTYPE html>409 An error occured. This email is already subscribed to the BotPanda daily briefing service.', 409
    elif result == 'invalid':
        return '<!DOCTYPE html>400 An error occured. Invalid email.', 400
    else:
        return 'An unknown error occured. Please report this in the support server at https://discord.gg/Zu6pDEBCjY'


@app.route('/contact', methods=['POST'])
@rate_limit(3, timedelta(minutes=1))
@rate_limit(5, timedelta(hours=1))
async def contact():
    form = await request.form
    email = form['email'].strip()
    name = form['name'].strip()
    message = form['message'].strip()
    result = await process_message(name, email, message)
    if result == 'success':
        return redirect(f'https://evilpanda.live/about/?success=true&email={email}&name={name}&message={message}')
    else:
        return redirect(f'https://evilpanda.live/about/?success=false&email={email}&name={name}&message={message}')


@app.route('/api/skyblock/dungeons')
@rate_limit(250, timedelta(hours=1))
async def dungeons():
    player = request.args['player'].strip()
    key = request.args['key'].strip()
    if key == await get_env_value('SKYBLOCK_API_KEY'):
        result = await get_dungeons(player)
        if result == 704 or result == 705 or result == 706:
            # These responses are still 200 success from HTTP perspective, even though they return an error
            if result == 704:
                return {'code': 704, 'error': 'Player not found.'}
            elif result == 705:
                return {'code': 705, 'error': 'Player has never joined hypixel.'}
            elif result == 706:
                return {'code': 706, 'error': 'Player has never joined skyblock.'}
        else:
            return result

@app.route('/api/skyblock/dungeons/party')
@rate_limit(50, timedelta(hours=1))
async def dungeon_party():
    players = request.args['players'].strip()
    key = request.args['key'].strip()
    if key == await get_env_value('SKYBLOCK_API_KEY'):
        players = players.split(',')
        if len(players) > 5:
            abort(400, 'Too many players, maximum is 5')
        else:
            result = await get_dungeon_party(players)
            return result




@app.after_request
def add_header(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['API-Version'] = '0.1'
    response.headers['Support'] = 'https://discord.gg/Zu6pDEBCjY'
    return response


if __name__ == '__main__':
    app.run(port=8080, use_reloader=False)


