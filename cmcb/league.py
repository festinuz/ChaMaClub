import asyncio
import time

import aiohttp

from . import utils
from . import static_data


DAY = static_data.DAY
REGIONS = static_data.LEAGUE_REGIONS
CACHE_UPDATE_TIMEOUT = static_data.LEAGUE_CACHE_UPDATE_TIMEOUT
REDIS_URL = static_data.REDIS_URL


class AsyncRateLeagueAPI:
    def __init__(self, api_key):
        self.api_key = api_key
        self.session = aiohttp.ClientSession()

    def __repr__(self):
        return 'ARLeagueAPI:{}'.format(self.api_key[-4:])

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
        API_URL_BASE = 'https://{platform}.api.riotgames.com/{api_url}'
        api_url = api_url.format(region=region, **kwargs)
        url = API_URL_BASE.format(platform=REGIONS[region], api_url=api_url)
        kwargs['api_key'] = self.api_key
        return self._session_get(url, params=kwargs)

    def get_summoner_by_name(self, region, summoner_name):
        url = '/lol/summoner/v3/summoners/by-name/{summonerName}'
        return self._request(url, region, summonerName=summoner_name)

    @utils.redis_timeout_cache(REDIS_URL, CACHE_UPDATE_TIMEOUT)
    async def get_summoner_revison_date(self, region, summoner):
        summoner = await self.get_summoner_by_name(region, summoner)
        try:
            return summoner['revisionDate']
        except KeyError:
            return None

    async def get_revision(self, region, summoner):
        out = str()
        revision_date = await self.get_summoner_revison_date(region, summoner)
        if revision_date not in ['None', None]:
            revision_date = int(revision_date)
            revision_date /= 1000
            days_ago = int((time.time() - revision_date)//DAY)
            if days_ago == 0:
                out = 'Today'
            else:
                out = utils.get_string_from_countable('day', days_ago) + ' ago'
        else:
            out = '*Never (not found)!*'
        return out
