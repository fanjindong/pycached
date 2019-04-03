import asyncio

from pycached import caches, SimpleMemoryCache, RedisCache
from pycached.serializers import StringSerializer, PickleSerializer

caches.set_config({
    'default': {
        'cache': "pycached.SimpleMemoryCache",
        'serializer': {
            'class': "pycached.serializers.StringSerializer"
        }
    },
    'redis_alt': {
        'cache': "pycached.RedisCache",
        'endpoint': "127.0.0.1",
        'port': 6379,
        'timeout': 1,
        'serializer': {
            'class': "pycached.serializers.PickleSerializer"
        },
        'plugins': [
            {'class': "pycached.plugins.HitMissRatioPlugin"},
            {'class': "pycached.plugins.TimingPlugin"}
        ]
    }
})


def default_cache():
    cache = caches.get('default')   # This always returns the same instance
    cache.set("key", "value")

    assert cache.get("key") == "value"
    assert isinstance(cache, SimpleMemoryCache)
    assert isinstance(cache.serializer, StringSerializer)


def alt_cache():
    # This generates a new instance every time! You can also use `caches.create('alt')`
    # or even `caches.create('alt', namespace="test", etc...)` to override extra args
    cache = caches.create(**caches.get_alias_config('redis_alt'))
    cache.set("key", "value")

    assert cache.get("key") == "value"
    assert isinstance(cache, RedisCache)
    assert isinstance(cache.serializer, PickleSerializer)
    assert len(cache.plugins) == 2
    assert cache.endpoint == "127.0.0.1"
    assert cache.timeout == 1
    assert cache.port == 6379
    cache.close()


def test_alias():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(default_cache())
    loop.run_until_complete(alt_cache())

    cache = RedisCache()
    loop.run_until_complete(cache.delete("key"))
    loop.run_until_complete(cache.close())

    loop.run_until_complete(caches.get('default').close())


if __name__ == "__main__":
    test_alias()
