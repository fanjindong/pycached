from unittest.mock import Mock, MagicMock, patch, ANY

import pytest

from redis import exceptions
from pycached import RedisCache
from pycached.backends.redis import RedisBackend, conn, REDIS_BEFORE_ONE
from pycached.base import BaseCache
from pycached.serializers import JsonSerializer


@pytest.fixture
def redis_connection():
    conn = MagicMock()
    conn.__enter__ = MagicMock(return_value=conn)
    conn.__exit__ = MagicMock()
    conn.get = Mock()
    conn.mget = Mock()
    conn.set = Mock()
    conn.setex = Mock()
    conn.mset = Mock()
    conn.incrby = Mock()
    conn.exists = Mock()
    conn.persist = Mock()
    conn.expire = Mock()
    conn.delete = Mock()
    conn.flushdb = Mock()
    conn.eval = Mock()
    conn.keys = Mock()
    conn.pipeline = MagicMock(return_value=conn)
    conn.execute = Mock()
    return conn


@pytest.fixture
def redis_pool(redis_connection):
    pool = redis_connection
    pool._conn = redis_connection
    pool.release = Mock()
    pool.clear = Mock()
    pool.acquire = Mock(return_value=redis_connection)
    pool.__call__ = MagicMock(return_value=pool)

    return pool


@pytest.fixture
def redis(redis_pool):
    redis = RedisBackend()
    redis._pool = redis_pool
    yield redis


@pytest.fixture
def create_pool():
    with patch("pycached.backends.redis.redis.Redis") as create_pool:
        yield create_pool


@pytest.fixture(autouse=True)
def mock_redis_v1(mocker, redis_connection):
    mocker.patch("pycached.backends.redis.redis.Redis", return_value=redis_connection)


class TestRedisBackend:
    def test_setup(self):
        redis_backend = RedisBackend()
        assert redis_backend.endpoint == "127.0.0.1"
        assert redis_backend.port == 6379
        assert redis_backend.db == 0
        assert redis_backend.password is None
        assert redis_backend.max_connections == 10

    def test_setup_override(self):
        redis_backend = RedisBackend(db=2, password="pass")

        assert redis_backend.endpoint == "127.0.0.1"
        assert redis_backend.port == 6379
        assert redis_backend.db == 2
        assert redis_backend.password == "pass"

    def test_setup_casts(self):
        redis_backend = RedisBackend(
            db="2",
            port="6379",
            max_connections="10",
            create_connection_timeout="1.5",
        )

        assert redis_backend.db == 2
        assert redis_backend.port == 6379
        assert redis_backend.max_connections == 10
        assert redis_backend.create_connection_timeout == 1.5

    def test_acquire_conn(self, redis, redis_connection):
        assert redis.acquire_conn() == redis_connection

    def test_release_conn(self, redis):
        conn = redis.acquire_conn()
        assert redis.release_conn(conn) is None

    def test_get_pool_sets_pool(self, redis, redis_pool, create_pool):
        redis._pool = None
        redis._get_pool()
        assert redis._pool == create_pool.return_value

    def test_get_pool_reuses_existing_pool(self, redis):
        redis._pool = "pool"
        redis._get_pool()
        assert redis._pool == "pool"

    def test_get_pool_calls_create_pool(self, redis, create_pool):
        redis._pool = None
        redis._get_pool()
        create_pool.assert_called_with(
            host=redis.endpoint,
            port=redis.port,
            db=redis.db,
            password=redis.password,
            connection_pool=None,
            encoding="utf-8",
            decode_responses=True,
            max_connections=redis.max_connections,
        )


    def test_get(self, redis, redis_connection):
        redis._get(pytest.KEY)
        redis_connection.get.assert_called_with(pytest.KEY)

    def test_gets(self, mocker, redis, redis_connection):
        mocker.spy(redis, "_get")
        redis._gets(pytest.KEY)
        redis._get.assert_called_with(pytest.KEY, _conn=ANY)

    def test_set(self, redis, redis_connection):
        redis._set(pytest.KEY, "value")
        redis_connection.set.assert_called_with(pytest.KEY, "value")

        redis._set(pytest.KEY, "value", ttl=1)
        redis_connection.setex.assert_called_with(pytest.KEY, 1, "value")

    def test_set_cas_token(self, mocker, redis, redis_connection):
        mocker.spy(redis, "_cas")
        redis._set(pytest.KEY, "value", _cas_token="old_value", _conn=redis_connection)
        redis._cas.assert_called_with(
            pytest.KEY, "value", "old_value", ttl=None, _conn=redis_connection
        )

    def test_cas(self, mocker, redis, redis_connection):
        mocker.spy(redis, "_raw")
        redis._cas(pytest.KEY, "value", "old_value", ttl=10, _conn=redis_connection)
        redis._raw.assert_called_with(
            "eval",
            redis.CAS_SCRIPT,
            [pytest.KEY],
            ["value", "old_value", "EX", 10],
            _conn=redis_connection,
        )

    def test_cas_float_ttl(self, mocker, redis, redis_connection):
        mocker.spy(redis, "_raw")
        redis._cas(pytest.KEY, "value", "old_value", ttl=0.1, _conn=redis_connection)
        redis._raw.assert_called_with(
            "eval",
            redis.CAS_SCRIPT,
            [pytest.KEY],
            ["value", "old_value", "PX", 100],
            _conn=redis_connection,
        )

    def test_multi_get(self, redis, redis_connection):
        redis._multi_get([pytest.KEY, pytest.KEY_1])
        redis_connection.mget.assert_called_with(pytest.KEY, pytest.KEY_1)

    def test_multi_set(self, redis, redis_connection):
        redis._multi_set([(pytest.KEY, "value"), (pytest.KEY_1, "random")])
        redis_connection.mset.assert_called_with({pytest.KEY: "value", pytest.KEY_1: "random"})

    def test_multi_set_with_ttl(self, redis, redis_connection):
        redis._multi_set([(pytest.KEY, "value"), (pytest.KEY_1, "random")], ttl=1)
        assert redis_connection.pipeline.call_count == 1
        redis_connection.mset.assert_called_with({pytest.KEY: "value", pytest.KEY_1: "random"})
        redis_connection.expire.assert_any_call(pytest.KEY, 1)
        redis_connection.expire.assert_any_call(pytest.KEY_1, 1)
        assert redis_connection.execute.call_count == 1

    def test_add(self, redis, redis_connection):
        redis._add(pytest.KEY, "value")
        redis_connection.set.assert_called_with(pytest.KEY, "value", exist=ANY, expire=None)

        redis._add(pytest.KEY, "value", 1)
        redis_connection.set.assert_called_with(pytest.KEY, "value", exist=ANY, expire=1)

    def test_add_existing(self, redis, redis_connection):
        redis_connection.set.return_value = False
        with pytest.raises(ValueError):
            redis._add(pytest.KEY, "value")

    def test_add_float_ttl(self, redis, redis_connection):
        redis._add(pytest.KEY, "value", 0.1)
        redis_connection.set.assert_called_with(pytest.KEY, "value", exist=ANY, pexpire=100)

    def test_exists(self, redis, redis_connection):
        redis_connection.exists.return_value = 1
        redis._exists(pytest.KEY)
        redis_connection.exists.assert_called_with(pytest.KEY)

    def test_expire(self, redis, redis_connection):
        redis._expire(pytest.KEY, ttl=1)
        redis_connection.expire.assert_called_with(pytest.KEY, 1)

    def test_increment(self, redis, redis_connection):
        redis._increment(pytest.KEY, delta=2)
        redis_connection.incrby.assert_called_with(pytest.KEY, 2)

    def test_increment_typerror(self, redis, redis_connection):
        redis_connection.incrby.side_effect = exceptions.RedisError("msg")
        with pytest.raises(TypeError):
            redis._increment(pytest.KEY, 2)

    def test_expire_0_ttl(self, redis, redis_connection):
        redis._expire(pytest.KEY, ttl=0)
        redis_connection.persist.assert_called_with(pytest.KEY)

    def test_delete(self, redis, redis_connection):
        redis._delete(pytest.KEY)
        redis_connection.delete.assert_called_with(pytest.KEY)

    def test_clear(self, redis, redis_connection):
        redis_connection.keys.return_value = ["nm:a", "nm:b"]
        redis._clear("nm")
        redis_connection.delete.assert_called_with("nm:a", "nm:b")

    def test_clear_no_namespace(self, redis, redis_connection):
        redis._clear()
        assert redis_connection.flushdb.call_count == 1

    def test_raw(self, redis, redis_connection):
        redis._raw("get", pytest.KEY)
        redis._raw("set", pytest.KEY, 1)
        redis_connection.get.assert_called_with(pytest.KEY)
        redis_connection.set.assert_called_with(pytest.KEY, 1)

    def test_redlock_release(self, mocker, redis):
        mocker.spy(redis, "_raw")
        redis._redlock_release(pytest.KEY, "random")
        redis._raw.assert_called_with("eval", redis.RELEASE_SCRIPT, [pytest.KEY], ["random"])

    def test_close_when_connected(self, redis):
        redis._raw("set", pytest.KEY, 1)
        assert redis._close() is None

    def test_close_when_not_connected(self, redis, redis_pool):
        redis._pool = None
        assert redis._close() is None


class TestConn:
    def dummy(self, *args, _conn=None, **kwargs):
        pass

    def test_conn(self, redis, redis_connection, mocker):
        mocker.spy(self, "dummy")
        d = conn(self.dummy)
        d(redis, "a", _conn=None)
        self.dummy.assert_called_with(redis, "a", _conn=redis_connection)

    def test_conn_reuses(self, redis, redis_connection, mocker):
        mocker.spy(self, "dummy")
        d = conn(self.dummy)
        d(redis, "a", _conn=redis_connection)
        self.dummy.assert_called_with(redis, "a", _conn=redis_connection)
        d(redis, "a", _conn=redis_connection)
        self.dummy.assert_called_with(redis, "a", _conn=redis_connection)

    @pytest.mark.parametrize(
        "path,expected", [("", {}), ("/", {}), ("/1", {"db": "1"}), ("/1/2/3", {"db": "1"})]
    )
    def test_parse_uri_path(self, path, expected):
        assert RedisBackend.parse_uri_path(path) == expected


class TestRedisCache:
    @pytest.fixture
    def set_test_namespace(self, redis_cache):
        redis_cache.namespace = "test"
        yield
        redis_cache.namespace = None

    def test_inheritance(self):
        assert isinstance(RedisCache(), BaseCache)

    def test_default_serializer(self):
        assert isinstance(RedisCache().serializer, JsonSerializer)

    @pytest.mark.parametrize(
        "namespace, expected",
        ([None, "test:" + pytest.KEY], ["", pytest.KEY], ["my_ns", "my_ns:" + pytest.KEY]),
    )
    def test_build_key_double_dot(self, set_test_namespace, redis_cache, namespace, expected):
        assert redis_cache.build_key(pytest.KEY, namespace=namespace) == expected

    def test_build_key_no_namespace(self, redis_cache):
        assert redis_cache.build_key(pytest.KEY, namespace=None) == pytest.KEY
