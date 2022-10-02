import types

class Helpers:

    @staticmethod
    def isProperty(obj, attr):
        return isinstance(getattr(type(obj), attr, None), property)
        
    @classmethod
    def transform(cls, this, attr, blacklist=None):
        blacklist = blacklist if blacklist is not None else []
        
        prototypes = [this.__class__] + (this.prototypes if hasattr(this, 'prototypes') else []) 
        T = None
        prototype = None
        for prototype in prototypes:
            prototype = prototype(this.row)

            if prototype in blacklist:
                continue
            blacklist.append(id(prototype))
            
            T = prototype.getTransformer(attr)

            if T is not None:
                break

        T = T if T is not None else lambda v, *args: v
        prototype = prototype if prototype is not None else this
        row = prototype.row
                
        return T(row[attr] if attr in row else None, attr, this.row)

    @classmethod
    def attribute(cls, this, attr, blacklist=None):
        blacklist = blacklist if blacklist is not None else [this]

        prototypes = this.prototypes if hasattr(this, 'prototypes') else [] 
        for prototype in prototypes:
            prototype = prototype(this.row)
            
            if prototype in blacklist:
                continue
            blacklist.append(prototype)

            if hasattr(prototype, attr):
                if Helpers.isProperty(prototype, attr):
                    prop = getattr(type(prototype), attr)
                    print(attr, prop.fget)
                val = getattr(prototype, attr)
                if (callable(val)):
                    val = types.MethodType(val.__func__, this)
                return val

        raise AttributeError('{} is missing'.format(attr))

        
    @staticmethod
    def eval(f, *args, **kwargs):
        if callable(f):
            return f(*args, **kwargs)
        return f

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

def createCache():

    cache = {}

    class Cache():

        @staticmethod
        def cacheKey(cls, row, prototypes):
            key = id(cls.__name__) + id(row)
            for p in prototypes:
                key += id(p)
            return key
        
        @classmethod
        def getCachedAs(cls, cacheKey):
            return cache.get(cacheKey, None)

        @classmethod
        def setCachedAs(cls, cacheKey, model):
            assert cls.getCachedAs(cacheKey) is None
            cache[cacheKey] = model 

    return Cache()
    



class As():

    @staticmethod
    def argStripper(f, argCount):

        def helper(*args):
            return f(*args[0:argCount])
        
        return helper
    
    columnSpecs = {}
    prototypes = []
    
    cache = createCache()

    @classmethod
    def cacheKey(cls, row, prototypes): 
        return cls.cache.cacheKey(cls, row, prototypes)
    
    @classmethod
    def create(cls, row: dict={}, prototypes: list=[]):
        return cls(row, prototypes)

    def __new__(cls, row: dict={}, prototypes: list=[]):
        if (isinstance(row, cls)):
            return cls.__new__(cls, row.row, prototypes)
        
        cacheKey = cls.cacheKey(row, prototypes + cls.prototypes)
        cachee = cls.cache.getCachedAs(cacheKey)
        if cachee is not None:
            return cachee

        res = super().__new__(cls)
        
        res.row = row
        res.prototypes = prototypes + cls.prototypes
        cls.cache.setCachedAs(cacheKey, res)
 
        return res
    
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

    def __getattr__(self, attr):
        return Helpers.attribute(self, attr)
    
    def __getitem__(self, attr):
        try:
            return Helpers.transform(self, attr)
        
        except Exception as e:
            print('\n-----------------')
            for key,val in Helpers.iterate(self.row):
                print(key, repr(val))
            print(attr)
            print('-----------------')
            raise e

    def __setitem__(self, key, val):
        self.row[key] = val

    def __len__(self):
        return len(self.row)

    def getTransformer(self, column):

        def pick(columnSpecs, column):
            if columnSpecs:
                columnSpec = columnSpecs[column] if column in columnSpecs else None
                if columnSpec:
                    return columnSpec['transformer'] if 'transformer' in columnSpec else None
            return None
            
        T = pick(self.__class__.columnSpecs, column)
        return T
        
    
    def keys(self):
        return self.row.keys()

