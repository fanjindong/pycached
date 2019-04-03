import asyncio

from pycached import RedisCache


cache = RedisCache(endpoint="127.0.0.1", port=6379, namespace="main")


def redis():
    cache.set("key", "value")
    cache.set("expire_me", "value", ttl=10)

    assert cache.get("key") == "value"
    assert cache.get("expire_me") == "value"
    assert cache.raw("ttl", "main:expire_me") > 0


def test_redis():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(redis())
    loop.run_until_complete(cache.delete("key"))
    loop.run_until_complete(cache.delete("expire_me"))
    loop.run_until_complete(cache.close())


if __name__ == "__main__":
    test_redis()
