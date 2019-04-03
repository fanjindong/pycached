import time

from pycached.backends import RedisCache, SimpleMemoryCache

def test_redisbackend():
    rb = RedisCache(endpoint="192.168.3.3")
    key = "test"
    rb.delete(key)
    assert rb.get(key) is None
    rb.set(key, 'a', ttl=1)
    assert rb.get(key) == 'a'
    time.sleep(1)
    assert rb.get(key) is None

def test_memory():
    cache = SimpleMemoryCache()
    key = 'test'
    cache.set(key, 'c', ttl=1)
    assert cache.get(key) == 'c'
    cache.set(key, 'd', ttl=1)
    assert cache.get(key) == 'd'
    time.sleep(1.2)
    assert cache.get(key) is None