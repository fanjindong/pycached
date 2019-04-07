from pycached import multi_cached, RedisCache

DICT = {
    'a': "Z",
    'b': "Y",
    'c': "X",
    'd': "W"
}


@multi_cached("ids", cache=RedisCache, namespace="main")
def multi_cached_ids(ids=None):
    return {id_: DICT[id_] for id_ in ids}


@multi_cached("keys", cache=RedisCache, namespace="main")
def multi_cached_keys(keys=None):
    return {id_: DICT[id_] for id_ in keys}


cache = RedisCache(endpoint="127.0.0.1", port=6379, namespace="main")


def test_multi_cached():
    multi_cached_ids(ids=['a', 'b'])
    multi_cached_ids(ids=['a', 'c'])
    multi_cached_keys(keys=['d'])

    assert cache.exists('a')
    assert cache.exists('b')
    assert cache.exists('c')
    assert cache.exists('d')

    cache.delete("a")
    cache.delete("b")
    cache.delete("c")
    cache.delete("d")
    cache.close()


if __name__ == "__main__":
    test_multi_cached()
