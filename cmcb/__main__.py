import asyncio

import league
import reddit
import utils
import website
import static_data


LEAGUE_API_KEY = static_data.LEAGUE_API_KEY
LEAGUE_REGIONS = static_data.LEAGUE_REGIONS

REDDIT_ID = static_data.REDDIT_CLIENT_ID
REDDIT_SECRET = static_data.REDDIT_CLIENT_SECRET
REDDIT_AGENT = static_data.REDDIT_USER_AGENT
REDDIT_NAME = static_data.REDDIT_USERNAME
REDDIT_PASS = static_data.REDDIT_PASSWORD
REDDIT_SUBREDDITS = static_data.REDDIT_SUBREDDITS
REDDIT_SUB_TIMEOUT = static_data.REDDIT_TO_PER_SUB
REDDIT_UPDATE_TIMEOUT = static_data.REDDIT_UPDATE_TIMEOUT

WEBSITE_URL = static_data.WEBSITE_URL

LOG_SUBREDDIT_UPDATES = static_data.LOG_SUBREDDIT_UPDATES
DEBUG_CLUB_PARSER = static_data.DEBUG_CLUB_PARSER

TEXT_HEAD = static_data.TEXT_HEAD
TEXT_REGION_TABLE = static_data.TEXT_REGION_TABLE
TEXT_CLUB_ROW = static_data.TEXT_CLUB_ROW
TEXT_EMPTY_REGIONS = static_data.TEXT_EMPTY_REGIONS
TEXT_BOTTOM = static_data.TEXT_BOTTOM


league_api = league.AsyncRateLeagueAPI(LEAGUE_API_KEY)
reddit_api = reddit.AsyncRateRedditAPI(
        client_id=REDDIT_ID, client_secret=REDDIT_SECRET,
        user_agent=REDDIT_AGENT, username=REDDIT_NAME, password=REDDIT_PASS)


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
        return TEXT_CLUB_ROW.format(self.club, self.permalink, self.tag,
                                    self.owner, self.opgg, self.revision)


@utils.logging(DEBUG_CLUB_PARSER)
def is_valid_club(comment_body):
    if len(comment_body) >= 5:
        if (
                comment_body[0].lower() == 'club' and
                comment_body[1].upper() in LEAGUE_REGIONS and
                len(comment_body[2]) < 20 and
                len(comment_body[3]) < 26 and
                2 < len(comment_body[4]) < 6 or comment_body[4] in ['-', '$']):
            return True
        else:
            return False


@utils.logging(DEBUG_CLUB_PARSER)
async def get_clubs_from_subreddit(submission_id):
    top_level_comments = await reddit_api.get_top_level_comments(submission_id)
    tlc = len(top_level_comments)
    clubs_by_regions = {region: list() for region in LEAGUE_REGIONS}
    for comment in top_level_comments:
        body = [i.strip() for i in comment.body.split('\n') if i != '']
        comment_is_club = is_valid_club(body)
        if comment_is_club:
            new_club = Club.create(body[1], body[2], body[3], body[4],
                                   comment.permalink())
            clubs_by_regions[body[1]].append(new_club)
    temp = [asyncio.gather(*clubs) for reg, clubs in clubs_by_regions.items()]
    region_clubs = await asyncio.gather(*temp)
    clubs_by_regions = {region: list() for region in LEAGUE_REGIONS}
    total = 0
    for clubs in region_clubs:
        for club in clubs:
            clubs_by_regions[club.region].append(club)
            total += 1
    return clubs_by_regions, tlc, total


@utils.logging(DEBUG_CLUB_PARSER)
def create_updated_text(subreddit, clubs_by_regions):
    updated_text = TEXT_HEAD.format(subreddit=subreddit)
    empty_regions = list()
    for region, clubs in sorted(clubs_by_regions.items(), key=lambda x: x[0]):
        if len(clubs):
            updated_text += TEXT_REGION_TABLE.format(region=region)
            updated_text += ''.join([str(club) for club in clubs])
        else:
            empty_regions.append(region)
    if len(empty_regions):
        updated_text += TEXT_EMPTY_REGIONS.format(
          empty_regions=', '.join(region for region in sorted(empty_regions)))
    updated_text += TEXT_BOTTOM
    return updated_text


@utils.logging(LOG_SUBREDDIT_UPDATES)
async def update_subreddit(subreddit):
    submission_id = REDDIT_SUBREDDITS[subreddit]
    clubs_by_regions, tlc, rc = await get_clubs_from_subreddit(submission_id)
    updated_text = create_updated_text(subreddit, clubs_by_regions)
    await reddit_api.edit_submission(submission_id, updated_text)
    return f'{subreddit}:{submission_id} updated. TLC: {tlc}, RC: {rc}'


async def update_subreddits(loop, subreddits):
    delay = REDDIT_SUB_TIMEOUT
    for subreddit in subreddits:
        await asyncio.gather(update_subreddit(subreddit), asyncio.sleep(delay))


async def main(loop):
    await website.HerokuWebsite.start(loop)
    website.HerokuWebsite.keep_awake(loop, WEBSITE_URL)
    while True:
        await asyncio.gather(update_subreddits(loop, REDDIT_SUBREDDITS),
                             asyncio.sleep(REDDIT_UPDATE_TIMEOUT))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main(loop))
