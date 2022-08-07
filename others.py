from aiohttp import ClientSession
from orjson import loads

from Dictionaries import unicode_regional_symbol


async def fetch(url: str, session: ClientSession) -> str:
    async with session.get(url) as request:
        return await request.text()


def get_city_state(city: dict) -> str:
    return city['state'] if 'state' in city else city['country']


def get_flag_emoji(country: str) -> str:
    return unicode_regional_symbol[country[0]] + unicode_regional_symbol[country[1]]
