from codesharer.utils.redis import RedisOrderedDict

class Snippets(RedisOrderedDict):
    def __init__(self, r):
        RedisHashMap.__init__(r, 'snippets')
    
