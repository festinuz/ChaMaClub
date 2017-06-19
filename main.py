import praw
from data.bot_data import DATA
from time import sleep


reddit = reddit = praw.Reddit(client_id=DATA['client_id'],
                              client_secret=DATA['client_secret'],
                              user_agent=DATA['user_agent'],
                              username=DATA['username'],
                              password=DATA['password'])

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
desired club or fill your club with some folks! Some additional info can be
found at the end of the post.\n
        '''.format(subreddit=subreddit)

        CLUB_TEXTFISH = '''\n
# Available {region} clubs:
Club name|Club tag|Owner IGN
:--|:--|:--\n'''
        potential_clubs = {region: list() for region in REGIONS}
        submission = reddit.submission(id=subreddits[subreddit])
        
        for top_level_comment in submission.comments:
            body = top_level_comment.body.split('\n')
            if body[0].lower() == 'club' and len(body) > 8:
                if body[2].upper() in potential_clubs:
                    potential_clubs[body[2].upper()].append(
                        (body[4], body[6], body[8])
                    )
                    
        for region, clubs in potential_clubs.items():
            if len(clubs) > 0:
                TEXTFISH += CLUB_TEXTFISH.format(region=region.upper())
                for club in clubs:
                    TEXTFISH += '{}|{}|{}\n'.format(club[1], club[2], club[0])

        END_OF_THE_POST = '''\n
This bot has just been created and is currently being tested. I would *love*
to hear your opinion! I have some extra things in mind that i will do if my
bot is at all needed, like checking last time club owner was online and stuff.
Anyways, here is how you can add your club: write a top level comment that
looks like this:


    club
        
    REGION CODE ({regions})
        
    YOUR IGN (used by people to send a friend request)
        
    CLUB NAME
        
    CLUB TAG (leave '-' if you dont have one yet)
        
You can always update info by updating your comment or delete your comment to
delete your club from a table. At the moment, the bot is set to update the
post every {seconds} seconds. If post hasn\'t been updated recently it means
the bot is currently offline. If this bot meets any success i\'ll put it on
24/7 host!'''.format(regions=','.join(REGIONS), seconds=SECONDS)
        submission.edit(TEXTFISH+END_OF_THE_POST)
    sleep(SECONDS)
