import aiohttp
import jinja2
import aiohttp_jinja2

import static_data


PORT = static_data.WEBSITE_PORT
TEMPLATES = static_data.WEBSITE_TEMPLATES_PATH


class HerokuWebsite:
    """Since heroku only allows for single website per application, this class
    is a singleton"""
    __server = None
    __routes = list()

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
        app = aiohttp.web.Application(loop=loop)
        for request_type, route, handler in HerokuWebsite.__routes:
            app.router.add_route(request_type, route, handler)
        aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(TEMPLATES))
        server = await loop.create_server(app.make_handler(), '0.0.0.0', PORT)
        HerokuWebsite.__server = server

    @staticmethod
    async def keep_awake(loop, url):
        """Heroku web applications hosted on free dyno plan are going into
        sleep mode if they haven't been accessed in a hour. To avoid this from
        happening, this function should be called at least once a hour with
        url being your heroku app url"""
        async with aiohttp.ClientSession(loop=loop) as client:
            async with client.get(url) as response:
                return await response.text()


@HerokuWebsite.route('GET', '/')
async def home(request):
    return aiohttp_jinja2.render_template("home.html", request, dict())


@HerokuWebsite.route('GET', '/about')
async def about(request):
    return aiohttp_jinja2.render_template("about.html", request, dict())
