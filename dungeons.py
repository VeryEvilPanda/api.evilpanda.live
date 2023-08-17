from utils import get_env_value
import aiohttp
import asyncio


async def get_dungeons(player):
    hypixel_key = await get_env_value("HYPIXEL_API_KEY")
    async with aiohttp.request('GET', f'https://api.ashcon.app/mojang/v2/user/{player}') as response:
        if response.status == 200:
            data = await response.json()
            uuid = data['uuid']
            username = data['username']
        else:
            # Custom error code for 'Player not found'
            return 704
    async with aiohttp.request('GET', f'https://api.hypixel.net/player?key={hypixel_key}&uuid={uuid}') as response:
                    data = await response.json()
                    if data['player']:
                        if 'skyblock_treasure_hunter' in data['player']['achievements']:
                            secrets_found = data['player']['achievements']['skyblock_treasure_hunter']
                        else:
                            secrets_found = 0
                    else:
                        # Custom error code for 'Player has never joined hypixel'
                        return 705
    async with aiohttp.request('GET', f'https://api.hypixel.net/skyblock/profiles?key={hypixel_key}&uuid={uuid}') as response:
        data = await response.json()
        uuid = uuid.replace('-', '')
        total_completions = 0
        profiles = data['profiles']
        if profiles:
            for profile in profiles:
                if profile['selected']:
                    active_profile = profile
            completions = active_profile['members'][uuid]['dungeons']['dungeon_types']['catacombs']['tier_completions']
            if completions == {}:
                f7 = 0
                total_completions = 0
            else:
                f7 = completions['7'] if '7' in completions else 0
                for floor in completions:
                    total_completions += completions[floor]
            return {'username': username, 'secrets_found': secrets_found, 'total_completions': total_completions, 'f7': f7}
        else:
            # Custom error code for 'Player has never joined skyblock'
            return 706



async def get_dungeon_party(players: list):
    hypixel_key = await get_env_value("HYPIXEL_API_KEY")
    players_stats = {}
    for player in players:
        async with aiohttp.request('GET', f'https://api.ashcon.app/mojang/v2/user/{player}') as response:
                if response.status == 200:
                    data = await response.json()
                    uuid = data['uuid']
                    username = data['username']
                    async with aiohttp.request('GET', f'https://api.hypixel.net/player?key={hypixel_key}&uuid={uuid}') as response:
                        data = await response.json()
                        if data['player']:
                            if 'skyblock_treasure_hunter' in data['player']['achievements']:
                                secrets_found = data['player']['achievements']['skyblock_treasure_hunter']
                            else:
                                secrets_found = 0
                            async with aiohttp.request('GET', f'https://api.hypixel.net/skyblock/profiles?key={hypixel_key}&uuid={uuid}') as response:
                                data = await response.json()
                                uuid = uuid.replace('-', '')
                                total_completions = 0
                                profiles = data['profiles']
                                if profiles:
                                    for profile in profiles:
                                        if profile['selected']:
                                            active_profile = profile
                                    completions = active_profile['members'][uuid]['dungeons']['dungeon_types']['catacombs']['tier_completions']
                                    if completions == {}:
                                        f7 = 0
                                        total_completions = 0
                                    else:
                                        f7 = completions['7'] if '7' in completions else 0
                                        for floor in completions:
                                            total_completions += completions[floor]
                                    players_stats[username] = {'secrets_found': secrets_found, 'total_completions': total_completions, 'f7': f7}
                                else:
                                    # Custom error code for 'Player has never joined skyblock.'
                                    players_stats[username] = {"code": 706, "error": "Player has never joined skyblock."}
                        else:
                            # Custom error code for 'Player has never joined hypixel.'
                            players_stats[username] = {"code": 705, "error": "Player has never joined hypixel."}
                    
                else:
                    # Custom error code for 'Player not found'
                    players_stats[player] = {"code": 704, "error": "Player not found."}
            
    return players_stats


        

   



