import os
# import time
import asyncio

import league
import reddit
import static_data


# league_api = league.AsyncRateLeagueAPI(api_key=os.environ['RIOT_API_KEY'])
reddit_api = reddit.RateRedditAPI(client_id=os.environ['CLIENT_ID'],
                                  client_secret=os.environ['CLIENT_SECRET'],
                                  user_agent=os.environ['USER_AGENT'],
                                  username=os.environ['USERNAME'],
                                  passwd=os.environ['PASSWORD'])


class Club:
    def __init__(self, region, owner_summoner_name, club_name, club_tag, link):
        self.region = region.upper()
        self.owner = reddit.escape_markdown(owner_summoner_name)
        self.club = reddit.escape_markdown(club_name)
        self.tag = reddit.escape_markdown(club_tag)
        self.permalink = link

    def __str__(self):
        return static_data.TEXT_CLUB_ROW.format(
          self.club, self.tag, self.owner, self.permalink)


async def get_clubs_from_subreddit(submission_id):
    top_level_comments = await reddit_api.get_top_level_comments(submission_id)
    clubs_by_regions = {region: list() for region in league.REGIONS}
    for comment in top_level_comments:
        body = comment.body.split('\n')
        comment_is_club = False
        if len(body) > 8:
            if (
                    body[0].lower() == 'club' and
                    body[2].upper() in league.REGIONS and
                    len(body[4]) < 20 and
                    len(body[6]) < 26 and
                    2 < len(body[8]) < 6 or body[8] in ['-', '$']):
                comment_is_club = True
        if comment_is_club:
            new_club = Club(body[2], body[4], body[6], body[8],
                            comment.permalink())
            clubs_by_regions[new_club.region].append(new_club)
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
      seconds=static_data.UPDATE_TIMEOUT)
    return updated_text


async def update_subreddit(subreddit):
    submission_id = static_data.SUBREDDITS[subreddit]
    clubs_by_regions = await get_clubs_from_subreddit(submission_id)
    updated_text = create_updated_text(subreddit, clubs_by_regions)
    await reddit_api.edit_submission(submission_id, updated_text)
    print(f'Subreddit {subreddit} updated.')


def update_subreddits(subreddits):
    return asyncio.gather(*[update_subreddit(sub) for sub in subreddits])


async def main():
    while True:
        await asyncio.gather(update_subreddits(static_data.SUBREDDITS),
                             asyncio.sleep(static_data.UPDATE_TIMEOUT))


if __name__ == '__main__':
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    # pending = asyncio.Task.all_tasks()
    # loop.run_until_complete(asyncio.gather(*pending))
