import asyncio

from asynctest import MagicMock

from pycached.base import BaseCache


def async_main():
    mocked_cache = MagicMock(spec=BaseCache)
    mocked_cache.get.return_value = "world"
    print(mocked_cache.get("hello"))


if __name__ == "__main__":
    loop = asyncio.get_event_loop()
    loop.run_until_complete(async_main())
