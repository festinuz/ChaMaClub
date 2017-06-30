from cmcb import reddit, static_data


ID = static_data.REDDIT_CLIENT_ID
SECRET = static_data.REDDIT_CLIENT_SECRET
AGENT = static_data.REDDIT_USER_AGENT
NAME = static_data.REDDIT_USERNAME
PASSWORD = static_data.REDDIT_PASSWORD


def test_api_ini():
    reddit_api = reddit.AsyncRateRedditAPI(ID, SECRET, AGENT, NAME, PASSWORD)
    print(reddit_api)
    assert True
