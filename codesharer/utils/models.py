import datetime
import pickle
import time
import uuid

from flask import g
from codesharer.utils.cache import cached_property
from codesharer.utils.redis import RedisHashMap, encode_key

class ModelDescriptor(type):
    def __new__(cls, name, bases, attrs):
        super_new = super(ModelDescriptor, cls).__new__
        parents = [b for b in bases if isinstance(b, ModelDescriptor)]
        if not parents:
            # If this isn't a subclass of Model, don't do anything special.
            return super_new(cls, name, bases, attrs)

        module = attrs.pop('__module__')
        new_class = super_new(cls, name, bases, {'__module__': module})
        attr_meta = attrs.pop('Meta', None)
        if not attr_meta:
            meta = getattr(new_class, 'Meta', None)
        else:
            meta = attr_meta
        setattr(new_class, '_meta', Options(new_class, meta, attrs))

        # Setup default manager
        setattr(new_class, 'objects', Manager(new_class))

        # Add all attributes to the class.
        for obj_name, obj in attrs.iteritems():
            setattr(new_class, obj_name, obj)

        return new_class

class Model(object):
    __metaclass__ = ModelDescriptor

    class DoesNotExist(Exception):
        pass

    def __init__(self, pk, **kwargs):
        self._storage = RedisHashMap(g.redis, '%s:items:%s' % (self._meta.db_name, pk))
        self.pk = pk
        for attname, field in self._meta.fields.iteritems():
            try:
                val = field.to_python(kwargs.pop(attname))
            except KeyError:
                # This is done with an exception rather than the
                # default argument on pop because we don't want
                # get_default() to be evaluated, and then not used.
                # Refs #12057.
                val = field.get_default()
            if val:
                setattr(self, attname, val)
        if kwargs:
            raise ValueError('%s are not part of the schema for %s' % (', '.join(kwargs.keys()), self.__class__.__name__))

    def __getattribute__(self, key):
        if key in object.__getattribute__(self, '_meta').fields:
            return self[key]
        return object.__getattribute__(self, key)

    def __setattr__(self, key, value):
        if key in object.__getattribute__(self, '_meta').fields:
            self[key] = value
        return object.__setattr__(self, key, value)

    def __getitem__(self, key):
        return self._storage[key]

    def __setitem__(self, key, value):
        field = self._meta.fields.get(key)
        if field:
            value = field.to_python(value)
        self._storage[key] = value

    def __repr__(self):
        return u'<%s: %s>' % (self.__class__.__name__, unicode(self))

    def __eq__(self, other):
        if type(self) != type(other):
            return False
        return self.pk == other.pk

    def __unicode__(self):
        return self.pk

    def __contains__(self, key):
        return key in self._storage

    def update(self, **kwargs):
        for k, v in kwargs.iteritems():
            self[k] = v

    def post_create(self):
        pass

class Options(object):
    def __init__(self, cls, meta, attrs):
        # Grab fields
        fields = []
        for obj_name, obj in attrs.iteritems():
            if isinstance(obj, Field):
                fields.append((obj_name, obj))

        self.fields = dict(fields)
        self.app_label = cls.__module__.split('.', 3)[1]
        self.module_name = cls.__name__
        if meta:
            self.indexes = list(meta.__dict__.get('indexes', []))
            self.db_name = meta.__dict__.get('db_name', '%s_%s' % (self.app_label, self.module_name))
        else:
            self.indexes = ()
            self.db_name = '%s_%s' % (self.app_label, self.module_name)

class Manager(object):
    def __init__(self, model):
        self.model = model
        self.name = encode_key(self.model._meta.db_name)

    def get(self, key):
        # XXX: ugly missing abstraction for key name
        if not g.redis.hlen('%s:items:%s' % (self.name, key)):
            raise self.model.DoesNotExist
        return self.model(pk=key)

    def get_many(self, keys):
        # XXX: ugly missing abstraction for key name
        results = []
        for key in keys:
            if not g.redis.hlen('%s:items:%s' % (self.name, key)):
                continue
            results.append(self.model(pk=key))
        return results

    def all(self, start=0, end=-1):
        for key in g.redis.zrevrange(self._get_default_index_key(), start, end):
            yield self.get(key)

    def count(self):
        return int(g.redis.get(self._get_default_count_key()) or 0)

    def for_index(self, index, key, start=0, end=-1):
        for id_ in g.redis.zrevrange(self._get_index_key(index, key), start, end):
            yield self.get(id_)

    def add_to_index(self, index, key, id_, score=None):
        g.redis.zadd(self._get_index_key(index, key), id_, score or time.time())
        g.redis.incr(self._get_index_count_key(index, key))
    
    def index_exists(self, index, key, id_):
        return g.redis.zscore(self._get_index_key(index, key), id_) != 0
        
    def create(self, **kwargs):
        for name, field in self.model._meta.fields.iteritems():
            if name not in kwargs and not field.default and field.required:
                raise ValueError('Missing required field: %s' % name)

        pk = kwargs.get('pk')
        if not pk:
            pk = uuid.uuid4().hex
        
        inst = self.model(pk=pk)
        
        inst.update(**kwargs)
        
        # Default index
        g.redis.zadd(self._get_default_index_key(), pk, time.time())        
        g.redis.incr(self._get_default_count_key())

        # Store additional predefined indexes
        for field in self.model._meta.indexes:
            if field in inst:
                self.add_to_index(field, getattr(inst, field), pk)

        inst.post_create()

        return inst

    @cached_property
    def storage(self):
        return RedisHashMap(g.redis, self._meta.db_name)

    def _get_index_key(self, index, key):
        return '%s:index:%s:%s' % (self.name, encode_key(index), encode_key(key))

    def _get_index_count_key(self, index, key):
        return '%s:count:%s:%s' % (self.name, encode_key(index), encode_key(key))

    def _get_default_index_key(self):
        return '%s:index:default' % (self.name,)

    def _get_default_count_key(self):
        return '%s:count:default' % (self.name,)

class Field(object):
    def __init__(self, default=None, required=True, **kwargs):
        self.default = default
        self.required = required

    def get_default(self):
        if not self.default:
            value = None
        elif callable(self.default):
            value = self.default()
        else:
            value = self.default
        return value

    def to_db(self, value=None):
        if value is None:
            value = ''
        return value

    def to_python(self, value=None):
        return value

class String(Field):
    def to_python(self, value=None):
        if value:
            value = unicode(value)
        return value

class Integer(Field):
    def to_python(self, value=None):
        if value:
            value = int(value)
        else:
            value = 0
        return value

class Float(Field):
    def to_python(self, value=None):
        if value:
            value = float(value)
        else:
            value = 0.0
        return value

class DateTime(Field):
    def to_db(self, value=None):
        if isinstance(value, datetime.datetime):
            # TODO: coerce this to UTC
            value = value.isoformat()
        return value

    def to_python(self, value=None):
        if value and not isinstance(value, datetime.datetime):
            # TODO: coerce this to a UTC datetime object
            value = datetime.datetime.strptime(value, '%Y-%m-%dT%H:%M:%S.%f')
        return value

class List(Field):
    def to_db(self, value=None):
        if isinstance(value, (tuple, list)):
            value = pickle.dumps(value)
        return value

    def to_python(self, value=None):
        if isinstance(value, basestring):
            value = pickle.loads(value)
        return value