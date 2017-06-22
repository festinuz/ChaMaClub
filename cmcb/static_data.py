SUBREDDITS = {
    'VayneMains': '6i7wp9',
}

UPDATE_TIMEOUT = 60

TEXT_HEAD = '''
Hello, /r/{subreddit}! This post updates automatically to help you find
desired club or fill your club with some folks! You can find additional info
at the end of the post.\n\n--------\n
'''

TEXT_REGION_TABLE = '''
\n# Available {region} clubs:
Club name|Club tag|Owner IGN
:--|:--|:--
'''

TEXT_CLUB_ROW = '{}|{}|[{}]({} "go to comment")\n'

TEXT_EMPTY_REGIONS = '''
Unfortunately, there are no clubs awalible for following regions at the moment
: {empty_regions}\n'''

TEXT_BOTTOM = '''\n\n----------\n
## How to **join a club**
+ Find a club that you want to join
+ Add club owner to friends in League of legends
+ Ask club owner for a club invite


## How to **add your club** to a list
Write a new comment that looks like an example below:


    club

    REGION CODE ({regions})

    YOUR IGN (used by people to send a friend request)

    CLUB NAME

    CLUB TAG (leave '-' if you dont have one yet)


You can always update club information by updating your comment, as well as you
can delete your comment when your club is full.
\n--------\n
At the moment, the bot is set to update the post every {seconds} seconds. The
bot is currently hosted on Heroku and should be working 24/7!
'''
