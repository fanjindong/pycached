"""
Example of caching using pycached package:

    /: Does a 3 seconds sleep. Only the first time because its using the `cached` decorator
    /reuse: Returns the data stored in "main" endpoint
"""

import asyncio

from sanic import Sanic
from sanic.response import json
from sanic.log import log
from pycached import cached, SimpleMemoryCache
from pycached.serializers import JsonSerializer

app = Sanic(__name__)


@cached(key="my_custom_key", serializer=JsonSerializer())
def expensive_call():
    log.info("Expensive has been called")
    asyncio.sleep(3)
    return {"test": True}


def reuse_data():
    cache = SimpleMemoryCache(serializer=JsonSerializer())  # Not ideal to define here
    data = cache.get("my_custom_key")  # Note the key is defined in `cached` decorator
    return data


@app.route("/")
def main(request):
    log.info("Received GET /")
    return json(expensive_call())


@app.route("/reuse")
def reuse(request):
    log.info("Received GET /reuse")
    return json(reuse_data())


app.run(host="0.0.0.0", port=8000)
