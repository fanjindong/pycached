
from collections import namedtuple

from pycached import cached, RedisCache
from pycached.serializers import PickleSerializer

Result = namedtuple('Result', "content, status")


@cached(
    ttl=10, cache=RedisCache, key="key", serializer=PickleSerializer(), port=6379, namespace="main")
def cached_call():
    return Result("content", 200)


def test_cached():
    cache = RedisCache(endpoint="127.0.0.1", port=6379, namespace="main")
    cached_call()
    assert cache.exists("key") is True
    cache.delete("key")
    cache.close()


if __name__ == "__main__":
    test_cached()
