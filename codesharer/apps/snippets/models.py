import time
import uuid

from codesharer.utils.redis import RedisOrderedDict, RedisHashMap, encode_key

class Snippet(RedisHashMap):
    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        return u'<%s: %s>' % (self.__class__.__name__, unicode(self))
    
    def __str__(self):
        return self.id

class Snippets(RedisOrderedDict):
    def __init__(self, r):
        RedisOrderedDict.__init__(self, r, 'snippets')
    
    def __getitem__(self, key):
        return Snippet(self._r, '%s:%s' % (self._name, encode_key(key)))

    def __iter__(self, start=0, end=-1):
        for key in self._r.zrevrange(self._name, start, end):
            yield self[key]

    def create(self, **kwargs):
        key = uuid.uuid4().hex
        inst = Snippet(self._r, '%s:%s' % (self._name, encode_key(key)))
        inst['id'] = key
        inst.update(**kwargs)
        self[inst.id] = time.time()
        return inst
