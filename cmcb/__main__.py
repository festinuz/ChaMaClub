import asyncio

import league
import reddit
import static_data
import utils


SUBREDDITS = static_data.REDDIT_SUBREDDITS
print(f'Subreddits loaded: {SUBREDDITS}')
league_api = league.AsyncRateLeagueAPI(static_data.LEAGUE_API_KEY)
reddit_api = reddit.RateRedditAPI(
        client_id=static_data.REDDIT_CLIENT_ID,
        client_secret=static_data.REDDIT_CLIENT_SECRET,
        user_agent=static_data.REDDIT_USER_AGENT,
        username=static_data.REDDIT_USERNAME,
        passwd=static_data.REDDIT_PASSWORD)


class Club:
    @classmethod
    async def create(cls, region, summoner_name, club_name, club_tag, link):
        self = Club(region, summoner_name, club_name, club_tag, link)
        self.revision = await league_api.get_revision(region, summoner_name)
        return self

    def __init__(self, region, summoner_name, club_name, club_tag, link):
        self.region = region.upper()
        self.owner = utils.escape_reddit_markdown(summoner_name)
        self.club = utils.escape_reddit_markdown(club_name)
        if club_tag in ['-', '$']:
            self.tag = '*No tag yet!*'
        else:
            self.tag = utils.escape_reddit_markdown(club_tag)
        self.permalink = link
        self.opgg = f'https://{region}.op.gg/summoner/userName={summoner_name}'

    def __str__(self):
        return static_data.TEXT_CLUB_ROW.format(
          self.club, self.permalink, self.tag, self.owner, self.opgg,
          self.revision)


@utils.logging(static_data.DEBUG_CLUB_PARSER)
async def get_clubs_from_subreddit(submission_id):
    top_level_comments = await reddit_api.get_top_level_comments(submission_id)
    tlc = len(top_level_comments)
    clubs_by_regions = {region: list() for region in league.REGIONS}
    for comment in top_level_comments:
        body = [i.strip() for i in comment.body.split('\n') if i != '']
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
            clubs_by_regions[body[1]].append(new_club)
    temp = [asyncio.gather(*clubs) for reg, clubs in clubs_by_regions.items()]
    region_clubs = await asyncio.gather(*temp)
    clubs_by_regions = {region: list() for region in league.REGIONS}
    total = 0
    for clubs in region_clubs:
        for club in clubs:
            clubs_by_regions[club.region].append(club)
            total += 1
    return clubs_by_regions, tlc, total


def create_updated_text(subreddit, clubs_by_regions):
    updated_text = static_data.TEXT_HEAD
    empty_regions = list()
    for region, clubs in sorted(clubs_by_regions.items(), key=lambda x: x[0]):
        if len(clubs):
            updated_text += static_data.TEXT_REGION_TABLE.format(region=region)
            updated_text += ''.join([str(club) for club in clubs])
        else:
            empty_regions.append(region)
    if len(empty_regions):
        updated_text += static_data.TEXT_EMPTY_REGIONS.format(
          empty_regions=', '.join(region for region in sorted(empty_regions)))
    updated_text += static_data.TEXT_BOTTOM
    updated_text = updated_text.format(
      subreddit=subreddit, regions=', '.join(sorted(league.REGIONS)),
      redditRevision=static_data.REDDIT_UPDATE_TIMEOUT,
      leagueRevision=static_data.LEAGUE_UPDATE_TIMEOUT//static_data.MINUTE)
    return updated_text


@utils.logging(static_data.LOG_SUBREDDIT_UPDATES)
async def update_subreddit(subreddit):
    submission_id = SUBREDDITS[subreddit]
    clubs_by_regions, tlc, rc = await get_clubs_from_subreddit(submission_id)
    updated_text = create_updated_text(subreddit, clubs_by_regions)
    await reddit_api.edit_submission(submission_id, updated_text)
    return f'{subreddit}:{submission_id} updated. TLC: {tlc}, RC: {rc}'


async def update_subreddits(loop, subreddits):
    delay = static_data.REDDIT_TO_PER_SUB
    for subreddit in subreddits:
        await asyncio.gather(update_subreddit(subreddit), asyncio.sleep(delay))


async def main(loop):
    while True:
        await asyncio.gather(update_subreddits(loop, SUBREDDITS),
                             asyncio.sleep(static_data.REDDIT_UPDATE_TIMEOUT))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
