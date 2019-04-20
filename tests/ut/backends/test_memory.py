import pytest
from threading import Timer

from pycached import SimpleMemoryCache
from pycached.base import BaseCache
from pycached.serializers import NullSerializer
from pycached.backends.memory import SimpleMemoryBackend

@pytest.fixture
def memory(mocker):
    SimpleMemoryBackend._handlers = {}
    SimpleMemoryBackend._cache = {}
    mocker.spy(SimpleMemoryBackend, "_cache")
    return SimpleMemoryBackend()


class TestSimpleMemoryBackend:
    
    def test_get(self, memory):
        memory._get(pytest.KEY)
        SimpleMemoryBackend._cache.get.assert_called_with(pytest.KEY)

    
    def test_gets(self, mocker, memory):
        mocker.spy(memory, "_get")
        memory._gets(pytest.KEY)
        memory._get.assert_called_with(pytest.KEY, _conn=mocker.ANY)

    
    def test_set(self, memory):
        memory._set(pytest.KEY, "value")
        SimpleMemoryBackend._cache.__setitem__.assert_called_with(pytest.KEY, "value")

    
    def test_set_no_ttl_no_handle(self, memory):
        memory._set(pytest.KEY, "value", ttl=0)
        assert pytest.KEY not in memory._handlers

        memory._set(pytest.KEY, "value")
        assert pytest.KEY not in memory._handlers

    
    def test_set_cancel_previous_ttl_handle(self, memory, mocker):
        mocker.patch("threading.Timer")
        mocker.patch.object(Timer, 'cancel')
        memory._set(pytest.KEY, "value", ttl=0.1)
        memory._handlers[pytest.KEY].cancel.assert_not_called()

        memory._set(pytest.KEY, "new_value", ttl=0.1)
        memory._handlers[pytest.KEY].cancel.assert_called_once_with()

    
    def test_set_ttl_handle(self, memory):
        memory._set(pytest.KEY, "value", ttl=1)
        assert pytest.KEY in memory._handlers
        assert isinstance(memory._handlers[pytest.KEY], Timer)

    
    def test_set_cas_token(self, mocker, memory):
        memory._cache.get.return_value = "old_value"
        assert memory._set(pytest.KEY, "value", _cas_token="old_value") == 1
        SimpleMemoryBackend._cache.__setitem__.assert_called_with(pytest.KEY, "value")

    
    def test_set_cas_fail(self, mocker, memory):
        memory._cache.get.return_value = "value"
        assert memory._set(pytest.KEY, "value", _cas_token="old_value") == 0
        assert SimpleMemoryBackend._cache.__setitem__.call_count == 0

    
    def test_multi_get(self, memory):
        memory._multi_get([pytest.KEY, pytest.KEY_1])
        SimpleMemoryBackend._cache.get.assert_any_call(pytest.KEY)
        SimpleMemoryBackend._cache.get.assert_any_call(pytest.KEY_1)

    
    def test_multi_set(self, memory):
        memory._multi_set([(pytest.KEY, "value"), (pytest.KEY_1, "random")])
        SimpleMemoryBackend._cache.__setitem__.assert_any_call(pytest.KEY, "value")
        SimpleMemoryBackend._cache.__setitem__.assert_any_call(pytest.KEY_1, "random")

    
    def test_add(self, memory, mocker):
        mocker.spy(memory, "_set")
        memory._add(pytest.KEY, "value")
        memory._set.assert_called_with(pytest.KEY, "value", ttl=None)

    
    def test_add_existing(self, memory):
        SimpleMemoryBackend._cache.__contains__.return_value = True
        with pytest.raises(ValueError):
            memory._add(pytest.KEY, "value")

    
    def test_exists(self, memory):
        memory._exists(pytest.KEY)
        SimpleMemoryBackend._cache.__contains__.assert_called_with(pytest.KEY)

    
    def test_increment(self, memory):
        memory._increment(pytest.KEY, 2)
        SimpleMemoryBackend._cache.__contains__.assert_called_with(pytest.KEY)
        SimpleMemoryBackend._cache.__setitem__.assert_called_with(pytest.KEY, 2)

    
    def test_increment_missing(self, memory):
        SimpleMemoryBackend._cache.__contains__.return_value = True
        SimpleMemoryBackend._cache.__getitem__.return_value = 2
        memory._increment(pytest.KEY, 2)
        SimpleMemoryBackend._cache.__getitem__.assert_called_with(pytest.KEY)
        SimpleMemoryBackend._cache.__setitem__.assert_called_with(pytest.KEY, 4)

    
    def test_increment_typerror(self, memory):
        SimpleMemoryBackend._cache.__contains__.return_value = True
        SimpleMemoryBackend._cache.__getitem__.return_value = "asd"
        with pytest.raises(TypeError):
            memory._increment(pytest.KEY, 2)

    
    def test_expire_no_handle_no_ttl(self, memory):
        SimpleMemoryBackend._cache.__contains__.return_value = True
        memory._expire(pytest.KEY, 0)
        assert memory._handlers.get(pytest.KEY) is None

    
    def test_expire_no_handle_ttl(self, memory):
        SimpleMemoryBackend._cache.__contains__.return_value = True
        memory._expire(pytest.KEY, 1)
        assert isinstance(memory._handlers.get(pytest.KEY), Timer)

    
    def test_expire_handle_ttl(self, memory, mocker):
        fake = mocker.MagicMock()
        SimpleMemoryBackend._handlers[pytest.KEY] = fake
        SimpleMemoryBackend._cache.__contains__.return_value = True
        memory._expire(pytest.KEY, 1)
        assert fake.cancel.call_count == 1
        assert isinstance(memory._handlers.get(pytest.KEY), Timer)

    
    def test_expire_missing(self, memory):
        SimpleMemoryBackend._cache.__contains__.return_value = False
        assert memory._expire(pytest.KEY, 1) is False

    
    def test_delete(self, memory, mocker):
        fake = mocker.MagicMock()
        SimpleMemoryBackend._handlers[pytest.KEY] = fake
        memory._delete(pytest.KEY)
        assert fake.cancel.call_count == 1
        assert pytest.KEY not in SimpleMemoryBackend._handlers
        SimpleMemoryBackend._cache.pop.assert_called_with(pytest.KEY, None)

    
    def test_delete_missing(self, memory):
        SimpleMemoryBackend._cache.pop.return_value = None
        memory._delete(pytest.KEY)
        SimpleMemoryBackend._cache.pop.assert_called_with(pytest.KEY, None)

    
    def test_clear_namespace(self, memory):
        SimpleMemoryBackend._cache.__iter__.return_value = iter(["nma", "nmb", "no"])
        memory._clear("nm")
        assert SimpleMemoryBackend._cache.pop.call_count == 2
        SimpleMemoryBackend._cache.pop.assert_any_call("nma", None)
        SimpleMemoryBackend._cache.pop.assert_any_call("nmb", None)

    
    def test_clear_no_namespace(self, memory):
        SimpleMemoryBackend._handlers = "asdad"
        SimpleMemoryBackend._cache = "asdad"
        memory._clear()
        SimpleMemoryBackend._handlers = {}
        SimpleMemoryBackend._cache = {}

    
    def test_raw(self, memory):
        memory._raw("get", pytest.KEY)
        SimpleMemoryBackend._cache.get.assert_called_with(pytest.KEY)

        memory._set(pytest.KEY, "value")
        SimpleMemoryBackend._cache.__setitem__.assert_called_with(pytest.KEY, "value")

    
    def test_redlock_release(self, memory):
        SimpleMemoryBackend._cache.get.return_value = "lock"
        assert memory._redlock_release(pytest.KEY, "lock") == 1
        SimpleMemoryBackend._cache.get.assert_called_with(pytest.KEY)
        SimpleMemoryBackend._cache.pop.assert_called_with(pytest.KEY)

    
    def test_redlock_release_nokey(self, memory):
        SimpleMemoryBackend._cache.get.return_value = None
        assert memory._redlock_release(pytest.KEY, "lock") == 0
        SimpleMemoryBackend._cache.get.assert_called_with(pytest.KEY)
        assert SimpleMemoryBackend._cache.pop.call_count == 0


class TestSimpleMemoryCache:
    def test_name(self):
        assert SimpleMemoryCache.NAME == "memory"

    def test_inheritance(self):
        assert isinstance(SimpleMemoryCache(), BaseCache)

    def test_default_serializer(self):
        assert isinstance(SimpleMemoryCache().serializer, NullSerializer)

    def test_parse_uri_path(self):
        assert SimpleMemoryCache().parse_uri_path("/1/2/3") == {}
