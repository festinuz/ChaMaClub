# CMCBot

CMCBot is a bot designed to be hosted on heroku that automates submissions on subreddits by parsing replies and updating submission text at regular time intervals. In its current state, the bot is used to update a series of subreddits that originate from [/r/ChampionMains](http://www.reddit.com/r/ChampionMains).


It is possible, with minimal code adjustments, to set up the bot to update any reddit sumbission on regular basis. If you're willing to do so, here's some clarification on project structure:
* The aplication-specific logic is located in \_\_main\_\_.py. You should rewrite it how you see fit.
* static_data.py provides all the data that is used by other modules, such as app-specific variables.
* league.py is app-specific and is used a wrapper of [Riot Games API](https://developer.riotgames.com/) for League of legends
* reddit.py if a minimal api wrapper for pythons PRAW library.
* website.py is optional and can be used to set up a website on a same dyno (for example, bot homepage).
