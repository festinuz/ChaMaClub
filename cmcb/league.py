import asyncio

import aiohttp


API_URL_BASE = 'https://{region}.api.pvp.net/{api_url}'
REGIONS = {'BR', 'EUNE', 'EUW', 'JP', 'KR', 'LAN', 'LAS', 'NA', 'OCE', 'TR',
           'RU', 'PBE'}


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
