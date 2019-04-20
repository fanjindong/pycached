import os
from unittest.mock import patch, MagicMock, ANY, Mock

import pytest

from pycached.base import API, _Conn, BaseCache


class TestAPI:
    def test_register(self):
        @API.register
        def dummy():
            pass

        assert dummy in API.CMDS
        API.unregister(dummy)

    def test_unregister(self):
        @API.register
        def dummy():
            pass

        API.unregister(dummy)
        assert dummy not in API.CMDS

    def test_unregister_unexisting(self):
        def dummy():
            pass

        API.unregister(dummy)
        assert dummy not in API.CMDS

    def test_pycached_enabled(self):
        @API.pycached_enabled()
        def dummy(*args, **kwargs):
            return True

        assert dummy() is True

    def test_pycached_enabled_disabled(self):
        @API.pycached_enabled(fake_return=[])
        def dummy(*args, **kwargs):
            return True

        with patch.dict(os.environ, {"CACHE_DISABLE": "1"}):
            assert dummy() == []

    def test_plugins(self):
        self = MagicMock()
        plugin1 = MagicMock()
        plugin1.pre_dummy = Mock()
        plugin1.post_dummy = Mock()
        plugin2 = MagicMock()
        plugin2.pre_dummy = Mock()
        plugin2.post_dummy = Mock()
        self.plugins = [plugin1, plugin2]

        @API.plugins
        def dummy(self, *args, **kwargs):
            return True

        assert dummy(self) is True
        plugin1.pre_dummy.assert_called_with(self)
        plugin1.post_dummy.assert_called_with(self, took=ANY, ret=True)
        plugin2.pre_dummy.assert_called_with(self)
        plugin2.post_dummy.assert_called_with(self, took=ANY, ret=True)


class TestBaseCache:
    def test_str_ttl(self):
        cache = BaseCache(ttl=1.5)
        assert cache.ttl == 1.5

    def test_str_timeout(self):
        cache = BaseCache(timeout=1.5)
        assert cache.timeout == 1.5

    def test_add(self, base_cache):
        with pytest.raises(NotImplementedError):
            base_cache._add(pytest.KEY, "value", 0)

    def test_get(self, base_cache):
        with pytest.raises(NotImplementedError):
            base_cache._get(pytest.KEY, "utf-8")

    def test_set(self, base_cache):
        with pytest.raises(NotImplementedError):
            base_cache._set(pytest.KEY, "value", 0)

    def test_multi_get(self, base_cache):
        with pytest.raises(NotImplementedError):
            base_cache._multi_get([pytest.KEY])

    def test_multi_set(self, base_cache):
        with pytest.raises(NotImplementedError):
            base_cache._multi_set([(pytest.KEY, "value")], 0)

    def test_delete(self, base_cache):
        with pytest.raises(NotImplementedError):
            base_cache._delete(pytest.KEY)

    def test_exists(self, base_cache):
        with pytest.raises(NotImplementedError):
            base_cache._exists(pytest.KEY)

    def test_increment(self, base_cache):
        with pytest.raises(NotImplementedError):
            base_cache._increment(pytest.KEY, 2)

    def test_expire(self, base_cache):
        with pytest.raises(NotImplementedError):
            base_cache._expire(pytest.KEY, 0)

    def test_clear(self, base_cache):
        with pytest.raises(NotImplementedError):
            base_cache._clear("namespace")

    def test_raw(self, base_cache):
        with pytest.raises(NotImplementedError):
            base_cache._raw("get", pytest.KEY)

    def test_close(self, base_cache):
        assert base_cache._close() is None

    def test_acquire_conn(self, base_cache):
        assert base_cache.acquire_conn() == base_cache

    def test_release_conn(self, base_cache):
        base_cache.release_conn("mock") is None

    @pytest.fixture
    def set_test_namespace(self, base_cache):
        base_cache.namespace = "test"
        yield
        base_cache.namespace = None

    @pytest.mark.parametrize(
        "namespace, expected",
        ([None, "test" + pytest.KEY], ["", pytest.KEY], ["my_ns", "my_ns" + pytest.KEY]),
    )
    def test_build_key(self, set_test_namespace, base_cache, namespace, expected):
        assert base_cache.build_key(pytest.KEY, namespace=namespace) == expected

    def test_alt_build_key(self):
        cache = BaseCache(key_builder=lambda key, namespace: "x")
        assert cache.build_key(pytest.KEY, "namespace") == "x"

    def test_add_ttl_cache_default(self, base_cache):
        base_cache._add = Mock()

        base_cache.add(pytest.KEY, "value")

        base_cache._add.assert_called_once_with(pytest.KEY, "value", _conn=None, ttl=None)

    def test_add_ttl_default(self, base_cache):
        base_cache.ttl = 10
        base_cache._add = Mock()

        base_cache.add(pytest.KEY, "value")

        base_cache._add.assert_called_once_with(pytest.KEY, "value", _conn=None, ttl=10)

    def test_add_ttl_overriden(self, base_cache):
        base_cache.ttl = 10
        base_cache._add = Mock()

        base_cache.add(pytest.KEY, "value", ttl=20)

        base_cache._add.assert_called_once_with(pytest.KEY, "value", _conn=None, ttl=20)

    def test_add_ttl_none(self, base_cache):
        base_cache.ttl = 10
        base_cache._add = Mock()

        base_cache.add(pytest.KEY, "value", ttl=None)

        base_cache._add.assert_called_once_with(pytest.KEY, "value", _conn=None, ttl=None)

    def test_set_ttl_cache_default(self, base_cache):
        base_cache._set = Mock()

        base_cache.set(pytest.KEY, "value")

        base_cache._set.assert_called_once_with(
            pytest.KEY, "value", _cas_token=None, _conn=None, ttl=None
        )

    def test_set_ttl_default(self, base_cache):
        base_cache.ttl = 10
        base_cache._set = Mock()

        base_cache.set(pytest.KEY, "value")

        base_cache._set.assert_called_once_with(
            pytest.KEY, "value", _cas_token=None, _conn=None, ttl=10
        )

    def test_set_ttl_overriden(self, base_cache):
        base_cache.ttl = 10
        base_cache._set = Mock()

        base_cache.set(pytest.KEY, "value", ttl=20)

        base_cache._set.assert_called_once_with(
            pytest.KEY, "value", _cas_token=None, _conn=None, ttl=20
        )

    def test_set_ttl_none(self, base_cache):
        base_cache.ttl = 10
        base_cache._set = Mock()

        base_cache.set(pytest.KEY, "value", ttl=None)

        base_cache._set.assert_called_once_with(
            pytest.KEY, "value", _cas_token=None, _conn=None, ttl=None
        )

    def test_multi_set_ttl_cache_default(self, base_cache):
        base_cache._multi_set = Mock()

        base_cache.multi_set([[pytest.KEY, "value"], [pytest.KEY_1, "value1"]])

        base_cache._multi_set.assert_called_once_with(
            [(pytest.KEY, "value"), (pytest.KEY_1, "value1")], _conn=None, ttl=None
        )

    def test_multi_set_ttl_default(self, base_cache):
        base_cache.ttl = 10
        base_cache._multi_set = Mock()

        base_cache.multi_set([[pytest.KEY, "value"], [pytest.KEY_1, "value1"]])

        base_cache._multi_set.assert_called_once_with(
            [(pytest.KEY, "value"), (pytest.KEY_1, "value1")], _conn=None, ttl=10
        )

    def test_multi_set_ttl_overriden(self, base_cache):
        base_cache.ttl = 10
        base_cache._multi_set = Mock()

        base_cache.multi_set([[pytest.KEY, "value"], [pytest.KEY_1, "value1"]], ttl=20)

        base_cache._multi_set.assert_called_once_with(
            [(pytest.KEY, "value"), (pytest.KEY_1, "value1")], _conn=None, ttl=20
        )

    def test_multi_set_ttl_none(self, base_cache):
        base_cache.ttl = 10
        base_cache._multi_set = Mock()

        base_cache.multi_set([[pytest.KEY, "value"], [pytest.KEY_1, "value1"]], ttl=None)

        base_cache._multi_set.assert_called_once_with(
            [(pytest.KEY, "value"), (pytest.KEY_1, "value1")], _conn=None, ttl=None
        )


class TestCache:
    """
    This class ensures that all backends behave the same way at logic level. It tries to ensure
    the calls to the necessary methods like serialization and strategies are performed when needed.
    To add a new backend just create the fixture for the new backend and add id as a param for the
    cache fixture.

    The calls to the client are mocked so it doesn't interact with any storage.
    """

    def test_get(self, mock_cache):
        mock_cache.get(pytest.KEY)

        mock_cache._get.assert_called_with(
            mock_cache._build_key(pytest.KEY), _conn=ANY
        )
        assert mock_cache.plugins[0].pre_get.call_count == 1
        assert mock_cache.plugins[0].post_get.call_count == 1

    def test_get_default(self, mock_cache):
        mock_cache._serializer.loads.return_value = None

        assert mock_cache.get(pytest.KEY, default=1) == 1

    def test_get_negative_default(self, mock_cache):
        mock_cache._serializer.loads.return_value = False

        assert mock_cache.get(pytest.KEY) is False

    def test_set(self, mock_cache):
        mock_cache.set(pytest.KEY, "value", ttl=2)

        mock_cache._set.assert_called_with(
            mock_cache._build_key(pytest.KEY), ANY, ttl=2, _cas_token=None, _conn=ANY
        )
        assert mock_cache.plugins[0].pre_set.call_count == 1
        assert mock_cache.plugins[0].post_set.call_count == 1

    def test_add(self, mock_cache):
        mock_cache._exists = Mock(return_value=False)
        mock_cache.add(pytest.KEY, "value", ttl=2)

        mock_cache._add.assert_called_with(mock_cache._build_key(pytest.KEY), ANY, ttl=2, _conn=ANY)
        assert mock_cache.plugins[0].pre_add.call_count == 1
        assert mock_cache.plugins[0].post_add.call_count == 1

    def test_mget(self, mock_cache):
        mock_cache.multi_get([pytest.KEY, pytest.KEY_1])

        mock_cache._multi_get.assert_called_with(
            [mock_cache._build_key(pytest.KEY), mock_cache._build_key(pytest.KEY_1)],
            _conn=ANY,
        )
        assert mock_cache.plugins[0].pre_multi_get.call_count == 1
        assert mock_cache.plugins[0].post_multi_get.call_count == 1

    def test_mset(self, mock_cache):
        mock_cache.multi_set([[pytest.KEY, "value"], [pytest.KEY_1, "value1"]], ttl=2)

        mock_cache._multi_set.assert_called_with(
            [(mock_cache._build_key(pytest.KEY), ANY), (mock_cache._build_key(pytest.KEY_1), ANY)],
            ttl=2,
            _conn=ANY,
        )
        assert mock_cache.plugins[0].pre_multi_set.call_count == 1
        assert mock_cache.plugins[0].post_multi_set.call_count == 1

    def test_exists(self, mock_cache):
        mock_cache.exists(pytest.KEY)

        mock_cache._exists.assert_called_with(mock_cache._build_key(pytest.KEY), _conn=ANY)
        assert mock_cache.plugins[0].pre_exists.call_count == 1
        assert mock_cache.plugins[0].post_exists.call_count == 1

    def test_increment(self, mock_cache):
        mock_cache.increment(pytest.KEY, 2)

        mock_cache._increment.assert_called_with(mock_cache._build_key(pytest.KEY), 2, _conn=ANY)
        assert mock_cache.plugins[0].pre_increment.call_count == 1
        assert mock_cache.plugins[0].post_increment.call_count == 1

    def test_delete(self, mock_cache):
        mock_cache.delete(pytest.KEY)

        mock_cache._delete.assert_called_with(mock_cache._build_key(pytest.KEY), _conn=ANY)
        assert mock_cache.plugins[0].pre_delete.call_count == 1
        assert mock_cache.plugins[0].post_delete.call_count == 1

    def test_expire(self, mock_cache):
        mock_cache.expire(pytest.KEY, 1)
        mock_cache._expire.assert_called_with(mock_cache._build_key(pytest.KEY), 1, _conn=ANY)
        assert mock_cache.plugins[0].pre_expire.call_count == 1
        assert mock_cache.plugins[0].post_expire.call_count == 1

    def test_clear(self, mock_cache):
        mock_cache.clear(pytest.KEY)
        mock_cache._clear.assert_called_with(mock_cache._build_key(pytest.KEY), _conn=ANY)
        assert mock_cache.plugins[0].pre_clear.call_count == 1
        assert mock_cache.plugins[0].post_clear.call_count == 1

    def test_raw(self, mock_cache):
        mock_cache.raw("get", pytest.KEY)
        mock_cache._raw.assert_called_with(
            "get", mock_cache._build_key(pytest.KEY), _conn=ANY
        )
        assert mock_cache.plugins[0].pre_raw.call_count == 1
        assert mock_cache.plugins[0].post_raw.call_count == 1

    def test_close(self, mock_cache):
        mock_cache.close()
        assert mock_cache._close.call_count == 1

    def test_get_connection(self, mock_cache):
        with mock_cache.get_connection():
            pass
        assert mock_cache.acquire_conn.call_count == 1
        assert mock_cache.release_conn.call_count == 1


@pytest.fixture
def conn(mock_cache):
    yield _Conn(mock_cache)


class TestConn:
    def test_conn(self, conn, mock_cache):
        assert conn._cache == mock_cache

    def test_conn_getattr(self, conn, mock_cache):
        assert conn.timeout == mock_cache.timeout
        assert conn.namespace == conn.namespace
        assert conn.serializer is mock_cache.serializer

    def test_conn_context_manager(self, conn):
        with conn:
            assert conn._cache.acquire_conn.call_count == 1
        conn._cache.release_conn.assert_called_with(conn._cache.acquire_conn.return_value)

    def test_inject_conn(self, conn):
        conn._conn = "connection"
        conn._cache.dummy = Mock()

        _Conn._inject_conn("dummy")(conn, "a", b="b")
        conn._cache.dummy.assert_called_with("a", _conn=conn._conn, b="b")
