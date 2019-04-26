from pycached import Cache

cache = Cache(Cache.REDIS, endpoint="127.0.0.1", port=6379, namespace="main")


def redis():
    cache.set("key", "value")
    cache.set("expire_me", "value", ttl=10)

    assert cache.get("key") == "value"
    assert cache.get("expire_me") == "value"
    assert cache.raw("ttl", "main:expire_me") > 0


def test_redis():
    redis()
    cache.delete("key")
    cache.delete("expire_me")
    cache.close()


if __name__ == "__main__":
    test_redis()
