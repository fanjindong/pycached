import logging
import time

from pycached import RedisCache
from pycached.lock import RedLock

logger = logging.getLogger(__name__)
cache = RedisCache(endpoint='127.0.0.1', port=6379, namespace='main')


def expensive_function():
    logger.warning('Expensive is being executed...')
    time.sleep(1)
    return 'result'


def my_view():
    with RedLock(cache, 'key', lease=2):  # Wait at most 2 seconds
        result = cache.get('key')
        if result is not None:
            logger.info('Found the value in the cache hurray!')
            return result

        result = expensive_function()
        cache.set('key', result)
        return result


def concurrent():
    my_view()
    my_view()
    my_view()


def test_redis():
    concurrent()
    cache.delete('key')
    cache.close()


if __name__ == '__main__':
    test_redis()
