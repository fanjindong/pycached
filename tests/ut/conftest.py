from unittest import mock

import pytest

from pycached import caches, RedisCache
from pycached.base import BaseCache, API
from pycached.plugins import BasePlugin
from pycached.serializers import BaseSerializer


def pytest_configure():
    """
    Before pytest_namespace was being used to set the keys for
    testing but the feature was removed
    https://docs.pytest.org/en/latest/deprecations.html#pytest-namespace
    """
    pytest.KEY = "key"
    pytest.KEY_1 = "random"


@pytest.fixture(autouse=True)
def reset_caches():
    caches.set_config(
        {
            "default": {
                "cache": "pycached.SimpleMemoryCache",
                "serializer": {"class": "pycached.serializers.NullSerializer"},
            }
        }
    )


class MockCache(BaseCache):
    def __init__(self):
        super().__init__()
        self._add = mock.Mock()
        self._get = mock.Mock()
        self._gets = mock.Mock()
        self._set = mock.Mock()
        self._multi_get = mock.Mock(return_value=["a", "b"])
        self._multi_set = mock.Mock()
        self._delete = mock.Mock()
        self._exists = mock.Mock()
        self._increment = mock.Mock()
        self._expire = mock.Mock()
        self._clear = mock.Mock()
        self._raw = mock.Mock()
        self._redlock_release = mock.Mock()
        self.acquire_conn = mock.Mock()
        self.release_conn = mock.Mock()
        self._close = mock.Mock()


@pytest.fixture
def mock_cache(mocker):
    cache = MockCache()
    cache.timeout = 0.002
    mocker.spy(cache, "_build_key")
    for cmd in API.CMDS:
        mocker.spy(cache, cmd.__name__)
    mocker.spy(cache, "close")
    cache.serializer = mock.Mock(spec=BaseSerializer)
    cache.serializer.encoding = "utf-8"
    cache.plugins = [mock.Mock(spec=BasePlugin)]
    return cache


@pytest.fixture
def base_cache():
    return BaseCache()


@pytest.fixture
def redis_cache():
    cache = RedisCache()
    return cache
