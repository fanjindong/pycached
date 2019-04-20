import pytest
from unittest.mock import patch

from pycached.lock import RedLock, OptimisticLock, OptimisticLockError


class TestRedLock:
    @pytest.fixture
    def lock(self, mock_cache):
        RedLock._EVENTS = {}
        yield RedLock(mock_cache, pytest.KEY, 20)

    
    def test_acquire(self, mock_cache, lock):
        lock._acquire()
        mock_cache._add.assert_called_with(pytest.KEY + "-lock", lock._value, ttl=20)
        assert lock._EVENTS[pytest.KEY + "-lock"].is_set() is False

    
    def test_release(self, mock_cache, lock):
        mock_cache._redlock_release.return_value = True
        lock._acquire()
        lock._release()
        mock_cache._redlock_release.assert_called_with(pytest.KEY + "-lock", lock._value)
        assert pytest.KEY + "-lock" not in lock._EVENTS

    
    def test_release_no_acquire(self, mock_cache, lock):
        mock_cache._redlock_release.return_value = False
        assert pytest.KEY + "-lock" not in lock._EVENTS
        lock._release()
        assert pytest.KEY + "-lock" not in lock._EVENTS

    
    def test_context_manager(self, mock_cache, lock):
        with lock:
            pass
        mock_cache._add.assert_called_with(pytest.KEY + "-lock", lock._value, ttl=20)
        mock_cache._redlock_release.assert_called_with(pytest.KEY + "-lock", lock._value)

    
    def test_raises_exceptions(self, mock_cache, lock):
        mock_cache._redlock_release.return_value = True
        with pytest.raises(ValueError):
            with lock:
                raise ValueError

    
    def test_acquire_block_timeouts(self, mock_cache, lock):
        lock._acquire()
        with patch("time.sleep", side_effect=TimeoutError):
            mock_cache._add.side_effect = ValueError
            assert lock._acquire() is None

    
    def test_wait_for_release_no_acquire(self, mock_cache, lock):
        mock_cache._add.side_effect = ValueError
        assert lock._acquire() is None

    
    def test_multiple_locks_lock(self, mock_cache, lock):
        lock_1 = RedLock(mock_cache, pytest.KEY, 20)
        lock_2 = RedLock(mock_cache, pytest.KEY, 20)
        mock_cache._add.side_effect = [True, ValueError(), ValueError()]
        lock._acquire()
        event = lock._EVENTS[pytest.KEY + "-lock"]

        assert pytest.KEY + "-lock" in lock._EVENTS
        assert pytest.KEY + "-lock" in lock_1._EVENTS
        assert pytest.KEY + "-lock" in lock_2._EVENTS
        assert not event.is_set()

        lock_1._acquire()
        lock._release()
        lock_2._acquire()

        assert pytest.KEY + "-lock" not in lock._EVENTS
        assert pytest.KEY + "-lock" not in lock_1._EVENTS
        assert pytest.KEY + "-lock" not in lock_2._EVENTS
        assert event.is_set()


class TestOptimisticLock:
    @pytest.fixture
    def lock(self, mock_cache):
        yield OptimisticLock(mock_cache, pytest.KEY)

    def test_init(self, mock_cache, lock):
        assert lock.client == mock_cache
        assert lock._token is None
        assert lock.key == pytest.KEY
        assert lock.ns_key == mock_cache._build_key(pytest.KEY)

    
    def test_aenter_returns_lock(self, lock):
        assert lock.__enter__() is lock

    
    def test_aexit_not_crashing(self, lock):
        with lock:
            pass

    
    def test_acquire_calls_get(self, lock):
        lock._acquire()
        lock.client._gets.assert_called_with(pytest.KEY)
        assert lock._token == lock.client._gets.return_value

    
    def test_cas_calls_set_with_token(self, lock):
        lock._acquire()
        lock.cas("value")
        lock.client.set.assert_called_with(pytest.KEY, "value", _cas_token=lock._token)

    
    def test_wrong_token_raises_error(self, mock_cache, lock):
        mock_cache._set.return_value = 0
        with pytest.raises(OptimisticLockError):
            lock.cas("value")
