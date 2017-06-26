import os
import json
import asyncio

import league
import reddit
import static_data


SUBREDDITS = json.loads(os.environ['SUBREDDITS'])
print(f'Subreddits loaded: {SUBREDDITS}')
league_api = league.AsyncRateLeagueAPI(api_key=os.environ['RIOT_API_KEY'])
reddit_api = reddit.RateRedditAPI(client_id=os.environ['CLIENT_ID'],
                                  client_secret=os.environ['CLIENT_SECRET'],
                                  user_agent=os.environ['USER_AGENT'],
                                  username=os.environ['USERNAME'],
                                  passwd=os.environ['PASSWORD'])


class Club:
    @classmethod
    async def create(cls, region, summoner_name, club_name, club_tag, link):
        self = Club(region, summoner_name, club_name, club_tag, link)
        self.revision = await league_api.get_revision(region, summoner_name)
        return self

    def __init__(self, region, summoner_name, club_name, club_tag, link):
        self.region = region.upper()
        self.owner = reddit.escape_markdown(summoner_name)
        self.club = reddit.escape_markdown(club_name)
        if club_tag in ['-', '$']:
            self.tag = '*No tag yet!*'
        else:
            self.tag = reddit.escape_markdown(club_tag)
        self.permalink = link
        self.opgg = f'https://{region}.op.gg/summoner/userName={summoner_name}'

    def __str__(self):
        return static_data.TEXT_CLUB_ROW.format(
          self.club, self.permalink, self.tag, self.owner, self.opgg,
          self.revision)


async def get_clubs_from_subreddit(submission_id):
    top_level_comments = await reddit_api.get_top_level_comments(submission_id)
    clubs_by_regions = {region: list() for region in league.REGIONS}
    for comment in top_level_comments:
        body = [i for i in comment.body.split('\n') if i != '']
        print(body)
        comment_is_club = False
        if len(body) >= 5:
            if (
                    body[0].lower() == 'club' and
                    body[1].upper() in league.REGIONS and
                    len(body[2]) < 20 and
                    len(body[3]) < 26 and
                    2 < len(body[4]) < 6 or body[4] in ['-', '$']):
                comment_is_club = True
        if comment_is_club:
            new_club = Club.create(body[1], body[2], body[3], body[4],
                                   comment.permalink())
            clubs_by_regions[body[1].append(new_club)
    temp = [asyncio.gather(*clubs) for reg, clubs in clubs_by_regions.items()]
    region_clubs = await asyncio.gather(*temp)
    clubs_by_regions = {region: list() for region in league.REGIONS}
    for clubs in region_clubs:
        for club in clubs:
            clubs_by_regions[club.region].append(club)
    return clubs_by_regions


def create_updated_text(subreddit, clubs_by_regions):
    updated_text = static_data.TEXT_HEAD
    empty_regions = list()
    for region, clubs in clubs_by_regions.items():
        if len(clubs):
            updated_text += static_data.TEXT_REGION_TABLE.format(region=region)
            updated_text += ''.join([str(club) for club in clubs])
        else:
            empty_regions.append(region)
    if len(empty_regions):
        updated_text += static_data.TEXT_EMPTY_REGIONS.format(
          empty_regions=', '.join(region for region in empty_regions))
    updated_text += static_data.TEXT_BOTTOM
    updated_text = updated_text.format(
      subreddit=subreddit, regions=', '.join(league.REGIONS),
      redditRevision=static_data.REDDIT_UPDATE_TIMEOUT,
      leagueRevision=static_data.LEAGUE_UPDATE_TIMEOUT//static_data.MINUTE)
    return updated_text


async def update_subreddit(subreddit):
    submission_id = SUBREDDITS[subreddit]
    clubs_by_regions = await get_clubs_from_subreddit(submission_id)
    updated_text = create_updated_text(subreddit, clubs_by_regions)
    await reddit_api.edit_submission(submission_id, updated_text)
    print(f'Subreddit {subreddit} updated.')


def update_subreddits(subreddits):
    return asyncio.gather(*[update_subreddit(sub) for sub in subreddits])


async def main():
    while True:
        await asyncio.gather(update_subreddits(SUBREDDITS),
                             asyncio.sleep(static_data.REDDIT_UPDATE_TIMEOUT))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    # pending = asyncio.Task.all_tasks()
    # loop.run_until_complete(asyncio.gather(*pending))
