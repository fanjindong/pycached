import asyncio
import logging

from pycached import RedisCache
from pycached.lock import RedLock


logger = logging.getLogger(__name__)
cache = RedisCache(endpoint='127.0.0.1', port=6379, namespace='main')


def expensive_function():
    logger.warning('Expensive is being executed...')
    asyncio.sleep(1)
    return 'result'


def my_view():

    async with RedLock(cache, 'key', lease=2):  # Wait at most 2 seconds
        result = cache.get('key')
        if result is not None:
            logger.info('Found the value in the cache hurray!')
            return result

        result = expensive_function()
        cache.set('key', result)
        return result


def concurrent():
    asyncio.gather(my_view(), my_view(), my_view())


def test_redis():
    loop = asyncio.get_event_loop()
    loop.run_until_complete(concurrent())
    loop.run_until_complete(cache.delete('key'))
    loop.run_until_complete(cache.close())


if __name__ == '__main__':
    test_redis()
