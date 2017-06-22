import asyncio
import praw


class RateRedditAPI:
    def __init__(self, client_id, client_secret, user_agent, username, passwd):
        self._reddit = praw.Reddit(
          client_id=client_id, client_secret=client_secret,
          user_agent=user_agent, username=username, password=passwd)
        self.loop = asyncio.get_event_loop()

    async def get_submission(self, submission_id):
        return await self.loop.run_in_executor(
          self._reddit.submission(id=submission_id))

    async def get_top_level_comments(self, submission_id):
        return self.get_submission(submission_id).comments

    async def edit_submission(self, submission_id, updated_text):
        return self.get_submission(submission_id).comments
