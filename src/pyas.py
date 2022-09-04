import re

class Helpers:
    
    @staticmethod
    def eval(f, *args, **kwargs):
        if callable(f):
            return f(*args, **kwargs)
        return f
    
    @classmethod
    def treePick(cls, inst, keys):
        #print('treePick', repr(inst), keys)

        item = inst[keys[0]]
        if len(keys) <= 1:
            return item
        return cls.treePick(item, keys[1:])
    

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
    
class As():

    @staticmethod
    def argStripper(f, argCount):

        def helper(*args):
            return f(*args[0:argCount])
        
        return helper
    @classmethod
    def createFactory(cls):

        def _(row, *args, **kwargs):
            if isinstance(row, cls):
                return row
            return cls(row, *args, **kwargs)
        return _
        
    columnSpecs = {
    }
    
    cache = {}
    @classmethod
    def cacheKey(cls, row):
        return cls, id(row)
    @classmethod
    def getCachedAs(cls, row):
        return cls.cache.get((cls, id(row)), None)
    @classmethod
    def setCachedAs(cls, row, model):
        assert cls.getCachedAs(row) is None
        cls.cache[cls.cacheKey(row)] = model 

    
    @classmethod
    def create(cls, row, *args, **kwargs):
        if (isinstance(row, cls)):
            return row

        cachee = cls.getCachedAs(row)
        if cachee is not None:
            #print('Using cached model for:', row)
            return cachee
        return cls(row, *args, **kwargs)

    def __init__(self, row={}, columnSpecs=None):

        assert self.getCachedAs(row) is None

        if columnSpecs is not None:
            self.columnSpecs = columnSpecs

        self.row = row
        self.setCachedAs(row, self)
        #print('Caching model for:', row)
        
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
        if isinstance(attr, (tuple, list)):
            return Helpers.treePick(self, tuple(attr))
        try:
            textVal = self.row[attr] if attr in self.row else None
        except Exception as e:
            print('\n-----------------')
            for key,val in Helpers.iterate(self.row):
                print(key, repr(val))
            print(attr)
            print('-----------------')
            raise e
        
        return self._transform(attr, textVal)

    def __setitem__(self, key, val):
        self.row[key] = val

    def __len__(self):
        return len(self.row)

    def _transformer(self, column):
        cs = self.columnSpecs
        if cs:
            cs = cs[column] if column in cs else None
            if cs:
                cs = cs['T'] if 'T' in cs else None
                if cs:
                    return cs

        cs = self.__class__.columnSpecs
        if cs:
            cs = cs[column] if column in cs else None
            if cs:
                cs = cs['T'] if 'T' in cs else None
                if cs:
                    return cs

        return lambda val, *_, **__: val
        
    def _transform(self, attr, textVal):
        transformer = self._transformer(attr)
        return transformer(textVal, attr, self)
    
    def _creator(self, column):
        cs = self.columnSpecs
        if cs:
            cs = cs[column] if column in cs else None
            if cs:
                cs = cs['creator'] if 'creator' in cs else None
                if cs:
                    return cs

        cs = self.__class__.columnSpecs
        if cs:
            cs = cs[column] if column in cs else None
            if cs:
                cs = cs['creator'] if 'creator' in cs else None
                if cs:
                    return cs

        return lambda val, *_, **__: val
        
    def _create(self, key, val):
        creator = self._creator(key)
        return creator(val)

    def keys(self):
        return self.row.keys()

    def match(self, attrRegExpMap={}, compile=False, casters=str):
        for attr, regExp in attrRegExpMap.items():
            if not attr in self.row:
                return False
            cre = re.compile(regExp) if compile else regExp
            val = self[attr]
            if not cre.match(Helpers.eval(casters, val) if casters is not None else val):
                return False
        return True

