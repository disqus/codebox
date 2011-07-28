"""
codebox.utils.models
~~~~~~~~~~~~~~~~~~~~

:copyright: (c) 2011 DISQUS.
:license: Apache License 2.0, see LICENSE for more details.
"""

import datetime
import itertools
import pickle
import time
import uuid

from flask import g
from codebox import app
from codebox.utils.cache import cached_property
from codebox.utils.redis import RedisHashMap, encode_key

NotDefined = object()

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


class DoesNotExist(Exception):
    pass

class DuplicateKeyError(Exception):
    pass

class Model(object):
    __metaclass__ = ModelDescriptor

    DoesNotExist = DoesNotExist
    DuplicateKeyError = DuplicateKeyError

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
        # Store additional predefined index
        if (key,) in self._meta.index or (key,) in self._meta.unique:
            self.objects.add_to_index(self.pk, **{key: value})

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
        if len(kwargs) > 1:
            # Store composite indexes
            for fields in itertools.chain(self._meta.index, self._meta.unique):
                if all([f in kwargs for f in fields]):
                    idx_kwargs = dict((f, getattr(self, f)) for f in fields)
                    self.add_to_index(self.pk, **idx_kwargs)

    def delete(self):
        # Clear all indexes first
        #  Default index
        g.redis.zrem(self.objects._get_default_index_key(), self.pk)
        g.redis.decr(self.objects._get_default_count_key())

        #  Store additional predefined index
        for fields in itertools.chain(self._meta.index, self._meta.unique):
            idx_kwargs = dict((f, getattr(self, f)) for f in fields)
            self.objects.remove_from_index(self.pk, **idx_kwargs)

        # Clear out the hash table for object
        self._storage.clear()

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
            self.index = list(meta.__dict__.get('index', []))
            self.unique = list(meta.__dict__.get('unique', []))
            self.db_name = meta.__dict__.get('db_name', '%s_%s' % (self.app_label, self.module_name))
        else:
            self.index = ()
            self.unique = ()
            self.db_name = '%s_%s' % (self.app_label, self.module_name)

class QuerySet(object):
    """
    Iterates over ``func`` using start/end kwargs.
    """
    def __init__(self, model, key, func, is_keymap=False):
        self.model = model
        self.func = func
        self.key = key
        self.is_keymap = is_keymap
    
    def __getitem__(self, key):
        is_slice = isinstance(key, slice)
        if is_slice:
            assert key.step == 1 or key.step is None
            start = key.start
            stop = key.stop
        else:
            start = key
            stop = key + 1

        if stop == -1:
            num = stop
        else:
            num = start - stop
        results = list(self.func(self.key, start=start, num=num))
        if self.is_keymap:
            results = [self.model(pk=r) for r in results]
        
        if is_slice:
            return results
        return results[0]

    def __iter__(self):
        for r in self[0:-1]:
            yield r

class Manager(object):
    def __init__(self, model):
        self.model = model
        self.name = encode_key(self.model._meta.db_name)

    def exists(self, key=None, **kwargs):
        if kwargs:
            idx_key = self._get_index_key(**kwargs)
            # Index lookup
            if key is None:
                return bool(len(g.redis.zrange(idx_key, 0, 1)))
            return g.redis.zscore(idx_key, key) is not None
        # XXX: missing abstraction for key name
        return g.redis.hlen('%s:items:%s' % (self.name, key))

    def get(self, key):
        if not self.exists(key):
            raise self.model.DoesNotExist
        return self.model(pk=key)

    def get_many(self, keys):
        results = []
        for key in keys:
            if not self.exists(key):
                continue
            results.append(self.model(pk=key))
        return results

    def all(self):
        return QuerySet(self.model, self._get_default_index_key(), g.redis.zrevrange, True)

    def count(self):
        return int(g.redis.get(self._get_default_count_key()) or 0)

    def filter(self, **kwargs):
        # XXX: we should have some logic to ensure the indexes requested exist
        assert kwargs
        app.logger.debug('Filtering on index %r', self._get_index_key(**kwargs))
        return QuerySet(self.model, self._get_index_key(**kwargs), g.redis.zrevrange, True)

    def add_to_index(self, key, score=None, **kwargs):
        app.logger.debug('Adding %r to index %r', key, self._get_index_key(**kwargs))
        g.redis.zadd(self._get_index_key(**kwargs), key, score or time.time())
        g.redis.incr(self._get_index_count_key(**kwargs))

    def remove_from_index(self, key, score=None, **kwargs):
        app.logger.debug('Removing %r from index %r', key, self._get_index_key(**kwargs))
        g.redis.zrem(self._get_index_key(**kwargs), key)
        g.redis.decr(self._get_index_count_key(**kwargs))
    
    def get_or_create(self, defaults={}, **kwargs):
        try:
            result = self.filter(**kwargs)[0]
            created = False
        except IndexError:
            kwargs = kwargs.copy()
            kwargs.update(defaults)
            result = self.create(**kwargs)
            created = True
        return result, created
    
    def create(self, **kwargs):
        for name, field in self.model._meta.fields.iteritems():
            if name not in kwargs and field.default is NotDefined and field.required:
                raise ValueError('Missing required field: %s' % name)

        for fieldset in self.model._meta.unique:
            constraint = dict((k, kwargs.get(k)) for k in fieldset)
            if all(constraint.itervalues()) and self.exists(None, **constraint):
                raise self.model.DuplicateKeyError('Constraint found for %s' % constraint)

        pk = kwargs.get('pk')
        if not pk:
            pk = uuid.uuid4().hex
        
        inst = self.model(pk=pk)
        
        inst.update(**kwargs)
        
        # Default index
        g.redis.zadd(self._get_default_index_key(), inst.pk, time.time())        
        g.redis.incr(self._get_default_count_key())

        # Store additional predefined index
        for fields in itertools.chain(self.model._meta.index, self.model._meta.unique):
            idx_kwargs = dict((f, getattr(inst, f)) for f in fields)
            self.add_to_index(inst.pk, **idx_kwargs)

        inst.post_create()

        return inst

    @cached_property
    def storage(self):
        return RedisHashMap(g.redis, self._meta.db_name)

    def _get_index_key(self, **kwargs):
        assert kwargs
        idx_key = ':'.join('%s=%s' % (encode_key(k), encode_key(v)) for k, v in sorted(kwargs.items(), key=lambda x: x[0]))
        return '%s:index:%s' % (self.name, idx_key)

    def _get_index_count_key(self, **kwargs):
        assert kwargs
        idx_key = ':'.join('%s=%s' % (encode_key(k), encode_key(v)) for k, v in sorted(kwargs.items(), key=lambda x: x[0]))
        return '%s:count:%s' % (self.name, idx_key)

    def _get_default_index_key(self):
        return '%s:index:default' % (self.name,)

    def _get_default_count_key(self):
        return '%s:count:default' % (self.name,)

class Field(object):
    def __init__(self, default=NotDefined, required=True, **kwargs):
        self.default = default
        self.required = required

    def get_default(self):
        if self.default is NotDefined:
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

class Boolean(Field):
    def to_db(self, value=None):
        if not value:
            value = False
        return int(bool(value))
    
    def to_python(self, value=None):
        if not value:
            value = False
        return bool(int(value))