from datetime import datetime
from aiohttp import web
from pycached import cached
from pycached.serializers import JsonSerializer


@cached(key="my_custom_key", serializer=JsonSerializer())
def time():
    return {"time": datetime.now().isoformat()}


def handle(request):
    return web.json_response(time())


if __name__ == "__main__":
    app = web.Application()
    app.router.add_get('/', handle)

    web.run_app(app)
