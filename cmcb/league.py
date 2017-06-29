import asyncio
from time import time

import aiohttp

import static_data
import utils

API_URL_BASE = 'https://{platform}.api.riotgames.com/{api_url}'
REGIONS = {'BR', 'EUNE', 'EUW', 'JP', 'KR', 'LAN', 'LAS', 'NA', 'OCE', 'TR',
           'RU'}

PLATFORMS = {
    'BR':   'BR1',
    'EUNE': 'EUN1',
    'EUW':  'EUW1',
    'JP':   'JP1',
    'KR':   'KR',
    'LAN':  'LA1',
    'LAS':  'LA2',
    'NA':   'NA1',
    'OCE':  'OC1',
    'TR':   'TR1',
    'RU':   'RU',
}


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

    @utils.redis_timeout_cache(static_data.REDIS_URL,
                               static_data.LEAGUE_UPDATE_TIMEOUT)
    async def get_summoner_revison_date(self, region, summoner):
        summoner = await self.get_summoner_by_name(region, summoner)
        try:
            return summoner['revisionDate']
        except KeyError:
            return None

    async def get_revision(self, region, summoner):
        output = str()
        revision_date = await self.get_summoner_revison_date(region, summoner)
        if revision_date not in ['None', None]:
            revision_date = int(revision_date)
            revision_date /= 1000
            days_ago = int((time() - revision_date)//static_data.DAY)
            if days_ago == 0:
                output = 'Today'
            elif days_ago % 10 == 1 and days_ago != 11:
                output = f'{days_ago} day ago'
            else:
                output = f'{days_ago} days ago'
        else:
            output = '*Never (not found)!*'
        return output
