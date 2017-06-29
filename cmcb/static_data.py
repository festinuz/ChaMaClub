import os
import json


# General
SECOND = 1
MINUTE = 60*SECOND
HOUR = 60*MINUTE
DAY = 24*HOUR
WEEK = 7*DAY

# Logging
LOG_SUBREDDIT_UPDATES = bool(os.environ.get('LOG_SUBREDDIT_UPDATES', False))
DEBUG_CLUB_PARSER = bool(os.environ.get('DEBUG_CLUB_PARSER', False))

# Website
WEBSITE_PORT = os.environ.get('PORT', None) or 8080
WEBSITE_URL = 'https://chamaclubs.herokuapp.com/'
WEBSITE_TEMPLATES_PATH = 'cmcb/templates'

# Reddit
REDDIT_CLIENT_ID = os.environ['REDDIT_CLIENT_ID']
REDDIT_CLIENT_SECRET = os.environ['REDDIT_CLIENT_SECRET']
REDDIT_USER_AGENT = os.environ['REDDIT_USER_AGENT']
REDDIT_USERNAME = os.environ['REDDIT_USERNAME']
REDDIT_PASSWORD = os.environ['REDDIT_PASSWORD']
REDDIT_SUBREDDITS = json.loads(os.environ['SUBREDDITS'])
REDDIT_TO_PER_SUB = 10*SECOND
REDDIT_UPDATE_TIMEOUT = max(MINUTE, len(REDDIT_SUBREDDITS)*REDDIT_TO_PER_SUB)
REDDIT_MARKDOWN_CHARACTERS = '*+-_~#^=`[]()>/'

# League
LEAGUE_API_KEY = os.environ['LEAGUE_API_KEY']
LEAGUE_UPDATE_TIMEOUT = HOUR  # used by cache function as key expiration time

# Submission
TEXT_HEAD = '''
Hello, /r/{subreddit}! This post updates automatically to help you find
desired club or fill your club with some folks! You can find additional info
at the end of the post.\n\n--------\n
'''

TEXT_REGION_TABLE = '''
\n## Available **{region}** clubs:
Club name|Club tag|Owner IGN|Last time online
:--------|:-------|:--------|:---------------
'''

TEXT_CLUB_ROW = '[{}]({} "Go to comment")|{}|[{}]({} "Check on op.gg")|{}\n'

TEXT_EMPTY_REGIONS = '''
Unfortunately, there are no clubs available for following regions at the moment
: {empty_regions}\n'''

TEXT_BOTTOM = '''\n\n----------\n
### How to **join a club**
+ Find a club that you want to join in a table
+ Click on club name to go to the club owners comment
+ Add club owner to friends in League of legends
+ Ask club owner for a club invite


### How to **add your club** to a list
Write a new comment that looks like below (note that each statement starts with
a new line):


    club  (this line tells the bot that this comment is possibly a club)
    REGION CODE ({regions})
    YOUR IGN (used by people to send a friend request)
    CLUB NAME
    CLUB TAG (leave '$' if you dont have one yet)
    (optional) ADDITIONAL INFO (you can write anything you want here)


For example:


    club
    EUW
    ExSummonerName
    ExBestClub
    ExTag


If you did it correctly, your club will apear in the table of your clubs region
in {redditRevision} seconds.
You can always update club information by updating your comment, as well as you
can delete your comment when your club is full.
\n--------\n
At the moment, the bot is set to update the post every {redditRevision}
seconds. The "Last time online" column updates every {leagueRevision} minutes.
The bot is currently hosted on Heroku and should be working 24/7! **If you have
a suggestion, feature request or a problem, [send a PM to me](/u/festinuz)!**
'''
