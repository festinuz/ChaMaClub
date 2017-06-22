
import praw


class RateRedditAPI:
    def __init__(self, client_id, client_secret, user_agent, username, passwd):
        self._reddit = praw.Reddit(
          client_id=client_id, client_secret=client_secret,
          user_agent=user_agent, username=username, password=passwd)

    async def get_top_level_comments(self, submission_id):
        submission = self._reddit.submission(id=submission_id)
        return submission.comments

    async def edit_submission(self, submission_id, updated_text):
        submission = self._reddit.submission(id=submission_id)
        submission.edit(updated_text)
