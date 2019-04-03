import random
import time

from pycached.backends import RedisCache
from pycached.decorators import cached


def test_cache():
    @cached(cache=RedisCache, endpoint='192.168.3.3', ttl=1)
    def fetch_random_number():
        return str(random.randint(1, 100000))

    resp_1 = fetch_random_number()
    resp_2 = fetch_random_number()
    time.sleep(1)
    resp_3 = fetch_random_number()

    assert resp_1 == resp_2
    assert resp_1 != resp_3
