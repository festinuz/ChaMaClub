from aiohttp import web
import jinja2
import aiohttp_jinja2

import static_data


PORT = static_data.WEBSITE_PORT

async def home(request):
    response = aiohttp_jinja2.render_template("home.html", request, dict())
    return response


async def about(request):
    response = aiohttp_jinja2.render_template("about.html", request, dict())
    return response


async def init(loop):
    app = web.Application(loop=loop)
    app.router.add_route('Get', '/', home)
    app.router.add_route('Get', '/about', about)
    templates_path = 'cmcb/templates'
    aiohttp_jinja2.setup(app, loader=jinja2.FileSystemLoader(templates_path))
    await loop.create_server(app.make_handler(), '0.0.0.0', PORT)
