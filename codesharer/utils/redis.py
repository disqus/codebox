import collections
import re

white = r'[\s&]+'

def encode_key(key):
    if isinstance(key, (list, tuple)):
        key = ' '.join(map(str, key))
    return re.sub(white, '_', str(key).strip())

class RedisOrderedDict(collections.MutableMapping):
    '''
    >>> from redis import Redis
    >>> r = Redis()
    >>> rod = RedisOrderedDict(r, 'test')
    >>> rod.get('bar')
    0
    >>> len(rod)
    0
    >>> rod['bar'] = 5.2
    >>> rod['bar']
    5.2000000000000002
    >>> len(rod)
    1
    >>> rod.items()
    [('bar', 5.2000000000000002)]
    >>> rod.clear()
    '''
    def __init__(self, r, name):
        self._r = r
        self._name = encode_key(name)
    
    def __iter__(self):
        return iter(self.items())
    
    def __len__(self):
        return self._r.zcard(self._name)
    
    def __getitem__(self, key):
        score = self._r.zscore(self._name, encode_key(key))
        values = self._r.hgetall(self.get_key(key))
        values['score'] = score
        return values
    
    def __setitem__(self, key, values):
        assert 'score' in values
        score = values['score']
        self._r.zadd(self._name, encode_key(key), score)
        
        hkey = self.get_key(key)
        for k, v in values.iteritems():
            if v == 'score':
                continue
            self._r.hset(hkey, k, v)
    
    def __delitem__(self, key):
        self._r.zrem(self._name, encode_key(key))
        self._r.delete(self.get_key(key))
    
    def get_key(self, key):
        return '%s:%s' % (self._name, encode_key(key))
    
    def keys(self, start=0, end=-1):
        # we use zrevrange to get keys sorted by high value instead of by lowest
        return self._r.zrevrange(self._name, start, end)
    
    def values(self, start=0, end=-1):
        return [v for (k, v) in self.items(start=start, end=end)]
    
    def items(self, start=0, end=-1):
        return self._r.zrevrange(self._name, start, end, withscores=True)
    
    def get(self, key, default=0):
        return self[key] or default
    
    def iteritems(self):
        return iter(self)
    
    def clear(self):
        self._r.delete(self._name)