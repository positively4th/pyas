import unittest
import re

from src.pyas import As
from src.pyas import Helpers

class TestAs(unittest.TestCase):

    def test_cache(self):
        class Testee(As):

            idInitCounter = {}
            
            def __new__(cls, row: dict, prototypes: list=[]):
                res = As.__new__(cls, row, prototypes)
                di = id(res)
                cls.idInitCounter[di] = cls.idInitCounter[di] if di in cls.idInitCounter else 0
                cls.idInitCounter[di] += 1
                return res
            
        row1 = {'a':1 , 'b':10}
        row2 = {'a':2 , 'b':20}
        row23 = {'a':2 , 'b':20}

        tm11 = Testee.create(row1)
        tm12 = Testee.create(row1)
        tm21 = Testee(row2)
        tm22 = Testee(row2)
        tm23 = Testee.create(row23)

        self.assertEqual(3, len(Testee.idInitCounter))
        instCnt = 0
        for di, cnt in Testee.idInitCounter.items():
            instCnt += cnt
        self.assertEqual(5, instCnt)

        self.assertEqual(tm11['a'], 1)
        self.assertEqual(tm11['b'], 10)
        self.assertEqual(tm12['a'], 1)
        self.assertEqual(tm12['b'], 10)

        self.assertEqual(tm21['a'], 2)
        self.assertEqual(tm21['b'], 20)
        self.assertEqual(tm22['a'], 2)
        self.assertEqual(tm22['b'], 20)
        self.assertEqual(tm23['a'], 2)
        self.assertEqual(tm23['b'], 20)

        row1['a'] *= -1 
        self.assertEqual(tm11['a'], -1)
        self.assertEqual(tm12['a'], -1)
        self.assertEqual(tm21['a'], 2)
        self.assertEqual(tm22['a'], 2)
        self.assertEqual(tm23['a'], 2)
       

    def testPrototypes(self):
        class Animal(As):
            columnSpecs = {
                'art': {
                    'transformer': lambda v, *args: 'Animal Art: ' + str(v)
                }
            }
            
            def __new__(cls, row: dict, prototypes: list=[]):
                res = super().__new__(cls, row,  prototypes)
                res._tag = cls.__name__ + ' Tag';
                return res
            def getTag(self):
                return self._tag
            @property
            def tag(self):
                return self._tag;
             
        class Vehicle(As):
            columnSpecs = {
                'brand': {
                    'transformer': lambda v, *args: 'Vehicle Brand: ' + str(v)
                }
            }
            def __new__(cls, row: dict, prototypes: list=[]):
                res = super().__new__(cls, row,  prototypes)
                res._tag = cls.__name__ + ' Tag';
                return res
            def getTag(self):
                return self._tag
            @property
            def tag(self):
                return self._tag;
            
        class MyVehicle(As):
            columnSpecs = {
                'brand': {
                    'transformer': lambda v, *args: 'My Vehicle Brand: ' + str(v)
                }
            }
            def __new__(cls, row: dict, prototypes: list=[]):
                res = super().__new__(cls, row,  prototypes)
                res._tag = cls.__name__ + ' Tag';
                return res
            def getTag(self):
                return self._tag
            @property
            def tag(self):
                return self._tag;
            
        class Car(As):
            columnSpecs = {
                'turbo': {
                    'transformer': lambda v, *args: 'Car Turbo: ' + ('Yes' if bool(v) else 'No') }
            }
            prototypes = [Vehicle]
            
        class Bike(As):
            columnSpecs = {
                'pedals': {
                    'transformer': lambda v, *args: 'Bike Pedals: ' + str(v)
                }
            }
            prototypes = [Vehicle]
            def __new__(cls, row: dict, prototypes: list=[]):
                res = super().__new__(cls, row,  prototypes)
                res._tag = cls.__name__ + ' Tag';
                return res
            def getTag(self):
                return self._tag
            @property
            def tag(self):
                return self._tag;
            
            
        dbs = { 'brand': 'DBS', 'pedals': 'Twin Turbo'}
        saab = { 'brand': 'SAAB', 'turbo': True}
        kia = { 'brand': 'KIA', 'turbo': False}
        lion = { 'art': 'Lion', 'turbo': True, 'pedals': 'Twin Turbo', 'brand': 'Nature'}
        saabee = Car(saab)
        kiaee = Car(kia)
        myKiaee = Car(kia, prototypes = [MyVehicle])
        lionee = Animal(lion, prototypes=[lambda row: Vehicle(row)])
        
        self.assertEqual(saabee['brand'], 'Vehicle Brand: SAAB')
        self.assertEqual(saabee['turbo'], 'Car Turbo: Yes')
        self.assertEqual(saabee.getTag(), 'Vehicle Tag') #Car has no tag
        self.assertEqual(saabee.tag, 'Vehicle Tag') #Car has no tag
        self.assertEqual(saabee._tag, 'Vehicle Tag') #Car has no tag

        self.assertEqual(kiaee['brand'], 'Vehicle Brand: KIA')
        self.assertEqual(kiaee['turbo'], 'Car Turbo: No')
        self.assertEqual(kiaee.getTag(), 'Vehicle Tag') #Car has no tag
        self.assertEqual(kiaee.tag, 'Vehicle Tag') #Car has no tag
        self.assertEqual(kiaee._tag, 'Vehicle Tag') #Car has no tag

        self.assertEqual(myKiaee['brand'], 'My Vehicle Brand: KIA')
        self.assertEqual(myKiaee['turbo'], 'Car Turbo: No')
        self.assertEqual(myKiaee.getTag(), 'MyVehicle Tag') #Car has no tag
        self.assertEqual(myKiaee.tag, 'MyVehicle Tag') #Car has no tag
        self.assertEqual(myKiaee._tag, 'MyVehicle Tag') #Car has no tag


        self.assertEqual(lionee['art'], 'Animal Art: Lion')
        self.assertEqual(lionee['brand'], 'Vehicle Brand: Nature')
        self.assertEqual(lionee['turbo'], True) 
        self.assertEqual(lionee['pedals'], 'Twin Turbo')
        self.assertEqual(lionee.getTag(), 'Animal Tag') #Car has no tag
        self.assertEqual(lionee.tag, 'Animal Tag') #Car has no tag
        self.assertEqual(lionee._tag, 'Animal Tag') #Car has no tag
            
       
    def testLegacy(self):
        #__seitem__
        
        class XGAs(As):
            columnSpecs = {
                'xG': {
                    'transformer': As.argStripper(float, 1)
                }
            }

            

            
        m = {
            'a': 1,
            'b': 2,
            'c': 3,
            }
        m['c'] = 33
        m['d'] = 44
        assert m['c'] == 33
        assert m['d'] == 44

        #iterate
        m = {
            'a': 1,
            'b': 2,
            'c': 3,
            }
        for key, val in Helpers.iterate(m):
            assert m[key] == val


        #Level 1 acces
        #ps = As.create({'xG': '1.1', 'name': 'test'}, transformers={'xG': As.argStripper(float, 1)})
        ps = As.create({'xG': '1.1', 'name': 'test'})
        #assert ps.xG == float('1.1')
        self.assertEqual(ps['xG'], '1.1')
        self.assertNotEqual(ps['xG'], float('1.1'))
        self.assertEqual(ps['name'], str('test'))
        #Level 1 acces
        ps = XGAs.create({'xG': '1.1', 'name': 'test'})
        #assert ps.xG == float('1.1')
        self.assertNotEqual(ps['xG'], '1.1')
        self.assertEqual(ps['xG'], float('1.1'))
        self.assertEqual(ps['name'], str('test'))


if __name__ == '__main__':
    unittest.main()

    
