"Thread-safe in-memory cache backend which doesn't use pickling."
 
# Example usage as a secondary cache:
#
# ## settings.py
# CACHES = {'default': {<your default cache settings>},
#           'inprocess': {'BACKEND': 'locmemnopickle.LocMemNoPickleCache'
#                         'KEY_PREFIX': 'my-prefix-',
#                         'TIMEOUT': 30}}
#
# ## myapp/views.py
# from django.core.cache import get_cache
# def myview(request):
#     cache = get_cache('inprocess')
#     key = generate_key(request)
#     data = cache.get(key)
#     if data is None:
#         data = generate_data(request)
#         cache.set(key, data)
#     return generate_response(data)

# This implementation has a twist. We introduced the infinite
# timeout conecpt introduced in Django 1.7.

import time

from django.core.cache.backends.base import BaseCache
from django.utils.synch import RWLock

# Stub class to ensure not passing in a `timeout` argument results in
# the default timeout
DEFAULT_TIMEOUT = object()

# Global in-memory store of cache data. Keyed by name, to provide
# multiple named local memory caches.
_caches = {}
_expire_info = {}
_locks = {}
 
class LocMemNoPickleCache(BaseCache):
    def __init__(self, name, params):
        BaseCache.__init__(self, params)
        global _caches, _expire_info, _locks
        self._cache = _caches.setdefault(name, {})
        self._expire_info = _expire_info.setdefault(name, {})
        self._lock = _locks.setdefault(name, RWLock())
 
    def get_backend_timeout(self, timeout=DEFAULT_TIMEOUT):
        """
        Returns the timeout value usable by this backend based upon the provided
        timeout.
        """
        if timeout == DEFAULT_TIMEOUT:
            timeout = self.default_timeout
        elif timeout == 0:
            # ticket 21147 - avoid time.time() related precision issues
            timeout = -1
        return None if timeout is None else time.time() + timeout

    def add(self, key, value, timeout=None, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        self._lock.writer_enters()
        try:
            if self._has_expired(key):
                self._set(key, value, timeout)
                return True
            return False
        finally:
            self._lock.writer_leaves()
 
    def get(self, key, default=None, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        self._lock.reader_enters()
        try:
            if not self._has_expired(key):
                return self._cache[key]
        finally:
            self._lock.reader_leaves()
        self._lock.writer_enters()
        try:
            try:
                del self._cache[key]
                del self._expire_info[key]
            except KeyError:
                pass
            return default
        finally:
            self._lock.writer_leaves()
 
    def _set(self, key, value, timeout=None):
        if len(self._cache) >= self._max_entries:
            self._cull()
        self._cache[key] = value
        self._expire_info[key] = self.get_backend_timeout(timeout)
 
    def set(self, key, value, timeout=None, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        self._lock.writer_enters()
        # Python 2.4 doesn't allow combined try-except-finally blocks.
        try:
            self._set(key, value, timeout)
        finally:
            self._lock.writer_leaves()
 
    def has_key(self, key, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        self._lock.reader_enters()
        try:
            if not self._has_expired(key):
                return True
        finally:
            self._lock.reader_leaves()
 
        self._lock.writer_enters()
        try:
            try:
                del self._cache[key]
                del self._expire_info[key]
            except KeyError:
                pass
            return False
        finally:
            self._lock.writer_leaves()
 
    def _has_expired(self, key):
        exp = self._expire_info.get(key, -1)
        if exp is None or exp > time.time():
            return False
        return True

    def _cull(self):
        if self._cull_frequency == 0:
            self.clear()
        else:
            doomed = [k for (i, k) in enumerate(self._cache) if i % self._cull_frequency == 0]
            for k in doomed:
                self._delete(k)
 
    def _delete(self, key):
        try:
            del self._cache[key]
        except KeyError:
            pass
        try:
            del self._expire_info[key]
        except KeyError:
            pass
 
    def delete(self, key, version=None):
        key = self.make_key(key, version=version)
        self.validate_key(key)
        self._lock.writer_enters()
        try:
            self._delete(key)
        finally:
            self._lock.writer_leaves()
 
    def clear(self):
        self._cache.clear()
        self._expire_info.clear()
 
# For backwards compatibility
class CacheClass(LocMemNoPickleCache):
    pass
