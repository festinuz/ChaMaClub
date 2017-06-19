import praw
from data.bot_data import DATA
from selftext import SELFTEXT


reddit = reddit = praw.Reddit(client_id=DATA['client_id'],
                              client_secret=DATA['client_secret'],
                              user_agent=DATA['user_agent'],
                              username=DATA['username'],
                              password=DATA['password'])

print(reddit.read_only)
subreddits = {
    'test': 'https://www.reddit.com/r/test/',
}

subreddit = reddit.subreddit('test')
# subreddit.submit('definitive bot testing', selftext=SELFTEXT)
# help(subreddit)
submission = reddit.submission(id='6i7ebc')
submission.edit(SELFTEXT)
for top_level_comment in submission.comments:
    print(top_level_comment.body)
