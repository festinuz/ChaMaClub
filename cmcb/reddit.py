import asyncio
import functools

import praw


class AsyncRateRedditAPI:
    def __init__(self, client_id, client_secret, user_agent, username,
                 password, loop=None):
        self._reddit = praw.Reddit(
          client_id=client_id, client_secret=client_secret,
          user_agent=user_agent, username=username, password=password)
        if loop is None:
            loop = asyncio.get_event_loop()
        self.loop = loop

    async def get_top_level_comments(self, submission_id):
        submission = await self.loop.run_in_executor(
          None, functools.partial(self._reddit.submission, id=submission_id))
        await self.loop.run_in_executor(
          None, functools.partial(submission.comments.replace_more, limit=None))
        return submission.comments

    async def edit_submission(self, submission_id, updated_text):
        submission = await self.loop.run_in_executor(
          None, functools.partial(self._reddit.submission, id=submission_id))
        await self.loop.run_in_executor(submission.edit, updated_text)
