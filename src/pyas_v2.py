import itertools
from collections import OrderedDict
from xxhash import xxh64


class T:

    @staticmethod
    def defWrapper(defVal, T0):
        def T(val, key, row, *args, **kwargs):

            if key not in row:
                assert val is None
                row[key] = defVal(val, key, row)
                return row[key]
            return T0(val, key, row, *args, **kwargs)

        return T


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


def As(*args, classBlacklist:list|tuple = ()):

    def buildClass(classlist: list | tuple):
        name = '_'.join(c.__name__ for c in classlist)
        newClass = type(name, tuple(classlist), {})
        newClass.prototypes = classlist
        return newClass

    _prototypes = list(OrderedDict.fromkeys(
        itertools.filterfalse(lambda cls: cls in classBlacklist,
                         itertools.chain(
                             *[
                                 [p] + (p.prototypes if hasattr(p, 'prototypes') else []) for p in (list(args) + [Root])
                             ]
                         ))))

    classCacheKey = Root.cache.classCacheKey(_prototypes)
    cachedClass = Root.cache.getCachedAs(classCacheKey)
    if cachedClass is None:
        cachedClass = buildClass(_prototypes)
        Root.cache.setCachedAs(classCacheKey, cachedClass)

    return cachedClass


class Leaf:
    prototypes = []


class Root:

    columnSpecs = {}
    prototypes = []

    cache = Helpers.createCache()

    @classmethod
    def onNew(cls, self):
        pass

    @staticmethod
    def classCacheKey(prototypes):
        return Root.cache.classCacheKey(prototypes)

    @classmethod
    def instanceCacheKey(cls, row, prototypes):
        return Root.cache.instanceCacheKey(cls, row, prototypes)

    #Todo: Remove, super() is correct method!.
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
            #assert instanceCacheKey == cachedClass.instanceCacheKey(
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
        return key in self.row

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
        return T(self.row[attr] if attr in self.row else None, attr, self.row)

    def __setitem__(self, key, val):
        self.row[key] = val

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


