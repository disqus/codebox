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

    def _get_user_key(self, user):
        return 'snippets:users:%s' % (encode_key(user),)

    def for_org(self, org, start, end):
        for key in RedisOrderedDict(r, self._get_org_key(org)).keys(start, end):
            yield self[key]

    def for_user(self, user, start, end):
        for key in RedisOrderedDict(r, self._get_user_key(user)).keys(start, end):
            yield self[key]

    def create(self, org, text, author, **kwargs):
        assert type(author) == int

        id_ = uuid.uuid4().hex

        inst = Snippet(self._r, self._get_item_key(id_))

        kwargs.update({
            'id': id_,
            'org': org,
            'text': text,
            'author': author,
            'created_at': time.time()
        })
        inst.update(**kwargs)

        # Store it in our primary index
        self.main[inst.id] = inst.created_at

        # Store it by organization
        # TODO: this is really fat, slim that shit up
        org = RedisOrderedDict(self._r, self._get_org_key(org))
        org[inst.id] = inst.created_at

        # Store it by user
        user = RedisOrderedDict(self._r, self._get_user_key(author))
        user[inst.id] = inst.created_at

        # XXX: Also need to store it for all members in organization

        return inst
