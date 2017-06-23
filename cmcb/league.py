import asyncio
from time import time
from functools import _make_key

import aiohttp

import static_data


API_URL_BASE = 'https://{region}.api.pvp.net/{api_url}'
REGIONS = {'BR', 'EUNE', 'EUW', 'JP', 'KR', 'LAN', 'LAS', 'NA', 'OCE', 'TR',
           'RU', 'PBE'}


def time_based_async_cache(async_function):
    cache = dict()
    timeout = static_data.HOUR

    async def wrapped_function(*args, **kwargs):
        key = _make_key(args, kwargs, False)
        cached_result = cache.get(key)
        if cached_result is not None:
            if time() - cached_result[0] < timeout:
                return cached_result
        result = await async_function(*args, **kwargs)
        cache[key] = (time(), result)
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
        url = API_URL_BASE.format(region=region, api_url=api_url)
        kwargs['api_key'] = self.api_key
        return self._session_get(url, params=kwargs)

    def get_summoner_by_name(self, region, summoner_name):
        url = '/lol/summoner/v3/summoners/by-name/{summonerName}'
        return self._request(url, region, summonerName=summoner_name)

    async def get_summoner_revision_date(self, region, summoner_name):
        summoner = await self.get_summoner_by_name(region, summoner_name)
        return summoner['revisionDate']

    @time_based_async_cache
    async def get_revision(self, region, summoner):
        output = str()
        revision_date = await self.get_summoner_revision_date(region, summoner)
        revision_date = revision_date/1000
        days_ago = (time() - revision_date)//static_data.DAY
        output = 'Today' if days_ago == 0 else output
        output = '1 day ago' if days_ago == 1 else output
        output = f'{days_ago} days ago' if days_ago > 1 else output
        return output
