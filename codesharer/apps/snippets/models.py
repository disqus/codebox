import time
import uuid

from codesharer.utils.redis import RedisOrderedDict, RedisHashMap, encode_key

class Snippet(RedisHashMap):
    pass

class Snippets(RedisOrderedDict):
    def __init__(self, r):
        RedisOrderedDict.__init__(self, r, 'snippets')
    
    def __getitem__(self, key):
        return Snippet(self._r, '%s:%s' % (self._name, encode_key(key)))

    def create(self, **kwargs):
        key = uuid.uuid4().hex
        inst = Snippet(self._r, '%s:%s' % (self._name, encode_key(key)))
        inst['id'] = key
        inst.update(**kwargs)
        self[inst.id] = time.time()
        return inst
