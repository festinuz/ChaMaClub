import praw
from os import environ
from time import sleep


reddit = reddit = praw.Reddit(client_id=environ['CLIENT_ID'],
                              client_secret=environ['CLIENT_SECRET'],
                              user_agent=environ['USER_AGENT'],
                              username=environ['USERNAME'],
                              password=environ['PASSWORD'])

print(reddit.read_only)
subreddits = {
    'VayneMains': '6i7wp9',
}

REGIONS = {'BR', 'EUNE', 'EUW', 'JP', 'KR', 'LAN', 'LAS', 'NA', 'OCE', 'TR',
           'RU', 'PBE'}

SECONDS = 60

while True:
    for subreddit in subreddits:
        TEXTFISH = '''
Hello, /r/{subreddit}! This post updates automatically to help you find
desired club or fill your club with some folks! You can find additional info
at the end of the post.

-----------

'''.format(subreddit=subreddit)

        CLUB_TEXTFISH = '''\n
# Available {region} clubs:
Club name|Club tag|Owner IGN
:--|:--|:--\n'''
        potential_clubs = {region: list() for region in REGIONS}
        submission = reddit.submission(id=subreddits[subreddit])

        for top_level_comment in submission.comments:
            body = top_level_comment.body.split('\n')
            comment_is_club = False
            if len(body) > 8:
                if (
                        body[0].lower() == 'club' and
                        body[2].upper() in potential_clubs and
                        len(body[4]) < 20 and
                        len(body[6]) < 26 and
                        len(body[8]) < 6):
                    comment_is_club = True
            if comment_is_club:
                potential_clubs[body[2].upper()].append(
                    (body[4], body[6], body[8],
                     top_level_comment.permalink()))

        for region, clubs in potential_clubs.items():
            if len(clubs) > 0:
                TEXTFISH += CLUB_TEXTFISH.format(region=region.upper())
                for club in clubs:
                    link = '[{}]({} "go to comment")'.format(club[0], club[3])
                    TEXTFISH += '{}|{}|{}\n'.format(club[1], club[2], link)

        END_OF_THE_POST = '''\n

----------

## How to **join a club**
+ Find a club that you want to join
+ Add club owner to friends in League of legends
+ Ask club owner for a club invite


## How to **add your club** to a list
+ Write a new comment that looks like an example below.


    club

    REGION CODE ({regions})

    YOUR IGN (used by people to send a friend request)

    CLUB NAME

    CLUB TAG (leave '-' if you dont have one yet)


You can always update club information by updating your comment, as well as you
can delete your comment when your club is full.

--------

At the moment, the bot is set to update the post every {seconds} seconds. The
bot is currently hosted on Heroku and should be working 24/7!
'''.format(regions=', '.join(REGIONS), seconds=SECONDS)
        submission.edit(TEXTFISH+END_OF_THE_POST)
    print('Post successfully updated!, totall comments parsed:',
          len(submission.comments))
    sleep(SECONDS)
