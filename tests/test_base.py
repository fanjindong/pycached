from pycached.base import BaseCache


def test_BaseCache():
    cache = BaseCache()
    assert cache.serializer
    assert cache.plugins == []