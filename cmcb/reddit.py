import praw


class AsyncRateRedditAPI:
    def __init__(self, client_id, client_secret, user_agent, username,
                 password):
        self._reddit = praw.Reddit(
          client_id=client_id, client_secret=client_secret,
          user_agent=user_agent, username=username, password=password)

    async def get_top_level_comments(self, submission_id):
        submission = self._reddit.submission(id=submission_id)
        submission.comments.replace_more(limit=None)
        # monkeypatch PRAW 5.2.0 bug
        comments = list()
        for comment in submission.comments:
            comment.body
            comments.append(comments)
        return comments

    async def edit_submission(self, submission_id, updated_text):
        submission = self._reddit.submission(id=submission_id)
        submission.edit(updated_text)
