import os
import asyncio
from time import time
from functools import _make_key

import aiohttp
import redis

import static_data

API_URL_BASE = 'https://{platform}.api.riotgames.com/{api_url}'
REGIONS = {'BR', 'EUNE', 'EUW', 'JP', 'KR', 'LAN', 'LAS', 'NA', 'OCE', 'TR',
           'RU', 'PBE'}

PLATFORMS = {
    'BR':   'BR1',
    'EUNE': 'EUN1',
    'EUW':  'EUW1',
    'JP':   'JP1',
    'KR':   'KR',
    'LAN':  'LA1',
    'LAS':  'LA2',
    'NA':   'NA',
    'OCE':  'OC1',
    'TR':   'TR1',
    'RU':   'RU',
    'PBE':  'PBE1',
}


def time_based_async_cache(async_function):
    cache = redis.from_url(os.environ['REDIS_URL'])

    async def wrapped_function(*args, **kwargs):
        key = _make_key(args, kwargs, False)
        cached_result = cache.get(key)
        if cached_result is not None:
            return cached_result
        result = await async_function(*args, **kwargs)
        cache.setex(key, result, static_data.LEAGUE_UPDATE_TIMEOUT)
        return result
    return wrapped_function


class AsyncRateLeagueAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = aiohttp.ClientSession()

    async def _session_get_simple(self, url, params):
        async with self.session.get(url, params=params) as response:
            return await response.json()

    async def _session_get(self, url, params):
        response = await self._session_get_simple(url, params)
        while response.get('status', dict()).get('status_code') == 429:
            await asyncio.sleep(1)
            response = await self._session_get_simple(url, params)
        return response

    def _request(self, api_url, region, **kwargs):
        api_url = api_url.format(region=region, **kwargs)
        url = API_URL_BASE.format(platform=PLATFORMS[region], api_url=api_url)
        kwargs['api_key'] = self.api_key
        return self._session_get(url, params=kwargs)

    def get_summoner_by_name(self, region, summoner_name):
        url = '/lol/summoner/v3/summoners/by-name/{summonerName}'
        return self._request(url, region, summonerName=summoner_name)

    @time_based_async_cache
    async def get_revision(self, region, summoner):
        output = str()
        summoner = await self.get_summoner_by_name(region, summoner)
        try:
            revision_date = summoner['revisionDate']
            revision_date = revision_date/1000
            days_ago = (time() - revision_date)//static_data.DAY
            if days_ago == 0:
                output = 'Today'
            elif days_ago % 10 == 1 and days_ago != 11:
                output = f'{days_ago} day ago'
            else:
                output = f'{days_ago} days ago'
        except KeyError:
            output = '*Never (not found)!*'
        return output
