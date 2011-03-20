from codesharer.utils.redis import RedisOrderedDict, RedisHashMap, encode_key

class Snippet(RedisHashMap):
    pass

class Snippets(RedisOrderedDict):
    def __init__(self, r):
        RedisOrderedDict.__init__(r, 'snippets')
    
    def __getitem__(self, key):
        return Snippet(self._r, '%s:%s' % (self._name, encode_key(key)))