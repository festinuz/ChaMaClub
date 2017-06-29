import asyncio

import aiohttp
import jinja2
import aiohttp_jinja2

import static_data


PORT = static_data.WEBSITE_PORT
TEMPLATES = static_data.WEBSITE_TEMPLATES_PATH


class HerokuWebsite:
    """Since heroku only allows for single website per application, this class
    is singleton-like and is used to get all revelant functions under one
    namespace."""
    __server = None
    __routes = list()
    __keep_awake_callback = None

    @staticmethod
    def route(request_type, route):
        def decorator(function):
            HerokuWebsite.__routes.append((request_type, route, function))
            return function
        return decorator

    @staticmethod
    async def start(loop):
        if HerokuWebsite.__server is not None:
            HerokuWebsite.__server.close()
            await HerokuWebsite.__server.wait_closed()
        if HerokuWebsite.__keep_awake_callback is not None:
            HerokuWebsite.__keep_awake_callback.cancel()
            HerokuWebsite.__keep_awake_callback = None
        app = aiohttp.web.Application(loop=loop)
        app.router.add_static('/static', 'cmcb/templates')
        for request_type, route, handler in HerokuWebsite.__routes:
            app.router.add_route(request_type, route, handler)
        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(TEMPLATES))
        server = await loop.create_server(app.make_handler(), '0.0.0.0', PORT)
        HerokuWebsite.__server = server

    @staticmethod
    async def get(loop, url):
        async with aiohttp.ClientSession(loop=loop) as client:
            async with client.get(url) as response:
                return await response.text()

    @staticmethod
    def keep_awake(loop, url):
        """Heroku web applications hosted on free dyno plan are going into
        sleep mode if they haven't been accessed in a hour.
        This function, called once, will send one GET request every 30 minutes,
        which will keep web app awake."""
        HerokuWebsite.__keep_awake_callback = loop.call_later(
            30*static_data.MINUTE, HerokuWebsite.keep_awake, loop, url)
        asyncio.ensure_future(HerokuWebsite.get(loop, url))


@HerokuWebsite.route('GET', '/')
async def home(request):
    context = {
      'subreddits_len': len(static_data.REDDIT_SUBREDDITS),
      'update_time': int(static_data.REDDIT_UPDATE_TIMEOUT)}
    return aiohttp_jinja2.render_template("index.html", request, context)


@HerokuWebsite.route('Get', '/riot.txt')
async def helo_rito(request):
    return aiohttp_jinja2.render_template("riot.txt", request, dict())
