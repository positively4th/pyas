from functools import wraps
from xxhash import xxh64
import ramda as R

semanticVersion = (3, 0, 0)


class PyasException(Exception):
    pass


class T:

    @staticmethod
    def _simpleSet(val, key, classee, *args, **kwargs):
        classee.row[key] = val

    @staticmethod
    def defWrapper(defVal, get):

        @wraps(get)
        def _get(val, key, classee, *args, **kwargs):

            if key not in classee:
                assert val is None
                classee.row[key] = defVal(val, key, classee)
                return classee.row[key]
            return get(val, key, classee, *args, **kwargs)

        return (_get, T._simpleSet)

    @staticmethod
    def writableEmpty(get):

        @wraps(get)
        def _get(val, key, classee, *args, **kwargs):

            if key not in classee.row:
                assert val is None
                classee.row[key] = get(val, key, classee, *args, **kwargs)

            return classee.row[key]

        return (_get, T._simpleSet)

    @staticmethod
    def constant(constant):

        def _get(val, key, classee, *args, **kwargs):

            _constant = constant(val, key, classee) if callable(
                constant) else constant

            if key not in classee.row:
                classee.row[key] = _constant
            else:
                if classee.row[key] != _constant:
                    raise PyasException(
                        'Wrong column {} constant value.'.format(key))

            return classee.row[key]

        def _set(val, key, classee, *args, **kwargs):

            _constant = constant(val, key, classee) if callable(
                constant) else constant

            if val != _constant:
                raise PyasException(
                    'Constant column {} can not be changed.'.format(key))

            if key in classee:
                if classee[key] != val:
                    raise PyasException(
                        'Constant column {} can not be changed.'.format(key))
            else:
                classee.row[key] = val

        return (_get, _set)

    @ staticmethod
    def constantNotEmpty():

        def _get(val, key, classee, *args, **kwargs):

            if key not in classee:
                raise PyasException('Missing column {}.'.format(key))
            return val

        def _set(val, key, classee, *args, **kwargs):

            if key not in classee.row:
                raise PyasException('Missing column {}.'.format(key))

            if classee.row[key] != val:
                raise PyasException(
                    'Constant column {} can not be changed.'.format(key))

        return (_get, _set)

    @ staticmethod
    def notEmpty(get):

        @ wraps(get)
        def _get(val, key, classee, *args, **kwargs):

            if key not in classee:
                raise PyasException('Missing column {}'.format(key))
            return get(val, key, classee, *args, **kwargs)

        return (_get, T._simpleSet)

    @ staticmethod
    def virtual(get: callable) -> tuple:

        @ wraps(get)
        def _get(val, key, classee, *args, **kwargs):

            if key in classee.row:
                raise PyasException(
                    'Virtual column {} has value.'.format(key))
            return get(val, key, classee, *args, **kwargs)

        def _set(val, key, classee, *args, **kwargs):
            raise PyasException(
                'Virtual column {} cannot be assigned.'.format(key))

        return (_get, _set)


class Helpers:

    @staticmethod
    def argStripper(f, argCount):

        def helper(*args):
            return f(*args[0:argCount])

        return helper

    @staticmethod
    def iterate(inst):
        if isinstance(inst, str):
            return {None: inst}.items()

        try:
            return inst.items()
        except AttributeError as e:
            pass
        except TypeError:
            pass

        try:
            return enumerate(inst)
        except TypeError:
            pass

        return {None: inst}.items()

    @staticmethod
    def createCache():
        cache = {}

        class Cache():

            @staticmethod
            def instanceCacheKey(cls, row, prototypes):
                key = xxh64()
                key.update(cls.__name__)
                key.update(str(id(row)))
                for p in prototypes:
                    key.update(p.__name__)
                return key.hexdigest()

            @staticmethod
            def classCacheKey(prototypes):
                key = 0
                for p in prototypes:
                    key += id(p)
                return key

            @classmethod
            def getCachedAs(cls, cacheKey):
                return cache.get(cacheKey, None)

            @classmethod
            def delCachedAs(cls, cacheKey):
                del cache[cacheKey]

            @classmethod
            def setCachedAs(cls, cacheKey, model):

                assert cls.getCachedAs(cacheKey) is None
                cache[cacheKey] = model

        return Cache()


def As(*args, classBlacklist: list | tuple = ()):

    def flattenGrabFirst(mixins, blacklist):
        return [key for key in [*dict.fromkeys(
            R.reduce(lambda res, mixin: res + [mixin] + (
                flattenGrabFirst(mixin.prototypes if hasattr(mixin, 'prototypes') else [], blacklist)), [])(mixins)
        )] if not key in blacklist]

    def buildClass(classlist: list | tuple):

        name = '_'.join(c.__name__ for c in classlist)
        newClass = type(name, tuple(classlist), {})
        newClass.prototypes = classlist
        for cls in classlist:
            if hasattr(cls, 'approveVersion') and not cls.approveVersion(semanticVersion):
                raise PyasException(
                    'Version {} is not approved by {}.'.format(semanticVersion, cls))
        return newClass

    _prototypes = flattenGrabFirst(list(args) + [Root], classBlacklist)

    classCacheKey = Root.cache.classCacheKey(_prototypes)
    cachedClass = Root.cache.getCachedAs(classCacheKey)
    if cachedClass is None:
        cachedClass = buildClass(_prototypes)
        Root.cache.setCachedAs(classCacheKey, cachedClass)

    return cachedClass


class Leaf:
    prototypes = []

    @classmethod
    def implements(cls, what):
        return what in cls.prototypes


class Root:

    columnSpecs = {}
    prototypes = []

    cache = Helpers.createCache()

    @staticmethod
    def approveVersion(_semanticVersion: tuple):
        return _semanticVersion[0] == semanticVersion[0]

    @classmethod
    def onNew(cls, self):
        pass

    @staticmethod
    def classCacheKey(prototypes):
        return Root.cache.classCacheKey(prototypes)

    @classmethod
    def instanceCacheKey(cls, row, prototypes):
        return Root.cache.instanceCacheKey(cls, row, prototypes)

    # Todo: Remove, super() is correct method!.
    @property
    def prototype(self):
        return super()

    def __new__(cls, row: dict = {}):

        if (isinstance(row, cls)):
            return row

        cachedClassKey = Root.cache.classCacheKey(cls.prototypes)
        cachedClass = Root.cache.getCachedAs(cachedClassKey)
        if cachedClass is None:
            cachedClass = As(*cls.prototypes)
        instanceCacheKey = cachedClass.instanceCacheKey(row, cls.prototypes)
        cachedInstnace = Root.cache.getCachedAs(instanceCacheKey)
        if cachedInstnace is not None:
            # assert instanceCacheKey == cachedClass.instanceCacheKey(
            #        cachedInstnace.row, cachedInstnace.prototypes), 'Cache error!'
            return cachedInstnace

        instance = object.__new__(cachedClass)

        instance.row = row
        for p in reversed(cls.prototypes):
            if hasattr(p, 'onNew'):
                p.onNew(instance)
        Root.cache.setCachedAs(instanceCacheKey, instance)

        return instance

    def __init__(self, row: dict = {}):
        pass

    def __str__(self, indent=''):
        return '{}({})'.format(indent, str(self.row))

    def __contains__(self, key):
        if key in self.row:
            return True
        T = self.getTransformer(
            key, self.__class__.prototypes)
        return T is not None

    def __iter__(self):

        class Iter():

            def __init__(self, models, index=0):
                self.models = models
                keys = list(models.row.keys())
                keys.sort()
                self.keys = keys[index:]

            def __iter__():
                return self

            def __next__(self):
                if len(self.keys) < 1:
                    raise StopIteration

                key = self.keys.pop(0)
                return key, self.models.row[key]

        return Iter(self, 0)

    def __getitem__(self, attr):
        T = Root.getTransformer(attr, self.__class__.prototypes)

        T = (lambda val, *args: val) if T is None else T
        T = T[0] if isinstance(T, (list, tuple)) else T
        return T(self.row[attr] if attr in self.row else None, attr, self)

    def __setitem__(self, key, val):

        def set(val, key, *args):
            self.row[key] = val

        T = Root.getTransformer(key, self.__class__.prototypes)
        T = T[1] if isinstance(T, (list, tuple)) and len(T) >= 2 else None
        T = set if T is None else T

        return T(val, key, self)

    def __len__(self):
        return len(self.row)

    @classmethod
    def getTransformer(cls, column, prototypes):

        def pick(cls, column):
            if not hasattr(cls, 'columnSpecs'):
                return None
            columnSpecs = cls.columnSpecs
            if not column in columnSpecs:
                return None
            columnSpec = columnSpecs[column]
            if not 'transformer' in columnSpec:
                return None
            return columnSpec['transformer']

        for prototype in prototypes:
            T = pick(prototype, column)
            if T is None:
                if len(prototype.__bases__):
                    for base in prototype.__bases__:
                        T = pick(base, column)
                        if T is not None:
                            break
            if T is not None:
                return T
        return None

    def keys(self):
        return self.row.keys()

    @property
    def columnNames(self):
        res = {}
        for p in reversed(self.prototypes):
            for c in p.columnSpecs.keys():
                res[c] = True
        return tuple(res.keys())

    def strip(self):
        res = {}
        for p in reversed(self.prototypes):
            for c in p.columnSpecs.keys():
                res[c] = self[c]
        return res
