SECOND = 1
MINUTE = 60*SECOND
HOUR = 60*MINUTE
DAY = 24*HOUR
WEEK = 7*DAY

REDDIT_UPDATE_TIMEOUT = MINUTE
LEAGUE_UPDATE_TIMEOUT = HOUR

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
a suggestion, feature request or a problem, [send a PM to me](/u/festinuz)!
'''
