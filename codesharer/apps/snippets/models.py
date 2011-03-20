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

class Snippets(object):
    def __init__(self, r):
        self._r = r
        self.main = RedisOrderedDict(r, 'snippets:global')

    def __getitem__(self, key):
        return Snippet(self._r, self._get_item_key(key))

    def __iter__(self, start=0, end=-1):
        for key in self.main.keys(start, end):
            yield self[key]

    def __len__(self):
        return len(self.main)
    
    def _get_item_key(self, id_):
        return 'snippets:items:%s' % (encode_key(id_),)

    def _get_org_key(self, org):
        return 'snippets:orgs:%s' % (encode_key(org),)

    def create(self, org, text, **kwargs):
        id_ = uuid.uuid4().hex
        inst = Snippet(self._r, self._get_item_key(id_))
        kwargs.update({
            'id': id_,
            'org': org,
            'text': text,
        })
        inst.update(**kwargs)
        self.main[inst.id] = time.time()
        return inst
