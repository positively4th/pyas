import unittest

from src.pyas_v3 import As
from src.pyas_v3 import Leaf
from src.pyas_v3 import Helpers


class TestGeneral(unittest.TestCase):

    def test_implements(self):

        class Red(Leaf):

            prototypes = []

            def describe(self):
                return '{} painted in {}'.format(super().describe(), 'Red')

        class Green(Leaf):

            prototypes = []

            def describe(self):
                return '{} painted in {}'.format(super().describe(), 'Red')

        class Blue(Leaf):
            prototypes = []

            def describe(self):
                return '{} painted in {}'.format(super().describe(), 'Blue')

        class Purple(Leaf):
            prototypes = []

            def describe(self):
                return '{} painted in {}'.format(super().describe(), 'Purple')

        class RGB(Leaf):
            prototypes = [Red, Blue, Green]

        self.assertTrue(As(RGB).implements(Red))
        self.assertTrue(As(RGB).implements(Green))
        self.assertTrue(As(RGB).implements(Blue))
        self.assertFalse(As(RGB).implements(Purple))

        self.assertTrue(As(Blue, Green, Red).implements(Red))
        self.assertTrue(As(Blue, Green, Red).implements(Green))
        self.assertTrue(As(Blue, Green, Red).implements(Blue))
        self.assertFalse(As(Blue, Green, Red).implements(Purple))

    def test_super(self):

        class Thing(Leaf):

            columnSpecs = {
                'name': {
                    'transformer': lambda v, k, row: v if k in row else None
                }
            }

            def describe(self):
                return 'A {}'.format(self['name'])

        class Red(Leaf):

            prototypes = []

            def describe(self):
                return '{} painted in {}'.format(super().describe(), 'Red')

        class StripedBlue(Leaf):
            prototypes = []

            def describe(self):
                return '{} with {} stripes'.format(super().describe(), 'Blue')

        exp = 'A house painted in Red with Blue stripes'
        act = As(StripedBlue, Red, Thing)({'name': 'house'}).describe()
        self.assertEqual(exp, act)
        exp = 'A house painted in Red'
        act = As(Red, Thing)({'name': 'house'}).describe()
        self.assertEqual(exp, act)
        exp = 'A house'
        act = As(Thing)({'name': 'house'}).describe()
        self.assertEqual(exp, act)

    def test_cache(self):
        class Testee(Leaf):

            idInitCounter = {}

            @classmethod
            def onNew(cls, self):
                di = id(self.row)
                cls.idInitCounter[di] = cls.idInitCounter[di] if di in cls.idInitCounter else 0
                cls.idInitCounter[di] += 1

        row1 = {'a': 1, 'b': 10}
        row2 = {'a': 2, 'b': 20}
        row23 = {'a': 2, 'b': 20}

        tm11 = As(Testee)(row1)
        tm12 = As(Testee)(row1)
        tm21 = As(Testee)(row2)
        tm22 = As(Testee)(row2)
        tm23 = As(Testee)(row23)

        self.assertEqual(3, len(Testee.idInitCounter))
        instCnt = 0
        for di, cnt in Testee.idInitCounter.items():
            instCnt += cnt
        self.assertEqual(3, instCnt)

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

    def test_prototypes(self):
        class Animal(Leaf):
            columnSpecs = {
                'art': {
                    'transformer': lambda v, *args: 'Animal Art: ' + str(v)
                }
            }

            @classmethod
            def onNew(cls, self):
                self._tag = cls.__name__ + ' Tag'

            def getTag(self):
                return self._tag

            @property
            def tag(self):
                return self._tag

        class Vehicle(Leaf):
            columnSpecs = {
                'brand': {
                    'transformer': lambda v, *args: 'Vehicle Brand: ' + str(v)
                }
            }

            @classmethod
            def onNew(cls, self):
                self._tag = cls.__name__ + ' Tag'

            def getTag(self):
                return self._tag

            @property
            def tag(self):
                return self._tag

        class MyVehicle(Leaf):
            columnSpecs = {
                'brand': {
                    'transformer': lambda v, *args: 'My Vehicle Brand: ' + str(v)
                }
            }

            @classmethod
            def onNew(cls, self):
                self._tag = cls.__name__ + ' Tag'

            def getTag(self):
                return self._tag

            @property
            def tag(self):
                return self._tag

        class Car(Leaf):
            columnSpecs = {
                'turbo': {
                    'transformer': lambda v, *args: 'Car Turbo: ' + ('Yes' if bool(v) else 'No')}
            }

        class Bike(Leaf):
            columnSpecs = {
                'pedals': {
                    'transformer': lambda v, *args: 'Bike Pedals: ' + str(v)
                }
            }

            @classmethod
            def onNew(cls, self):
                self._tag = cls.__name__ + ' Tag'

            def getTag(self):
                return self._tag

            @property
            def tag(self):
                return self._tag

        dbs = {'brand': 'DBS', 'pedals': 'Twin Turbo'}
        saab = {'brand': 'SAAB', 'turbo': True}
        kia = {'brand': 'KIA', 'turbo': False}
        lion = {'art': 'Lion', 'turbo': True,
                'pedals': 'Twin Turbo', 'brand': 'Nature'}
        saabee = As(Car, Vehicle)(saab)
        kiaee = As(Car, Vehicle)(kia)
        myKiaee = As(Car, MyVehicle)(kia)
        lionee = As(Animal, Vehicle)(lion)

        self.assertEqual(saabee['brand'], 'Vehicle Brand: SAAB')
        self.assertEqual(saabee['turbo'], 'Car Turbo: Yes')
        self.assertEqual(saabee.getTag(), 'Vehicle Tag')  # Car has no tag
        self.assertEqual(saabee.tag, 'Vehicle Tag')  # Car has no tag
        self.assertEqual(saabee._tag, 'Vehicle Tag')  # Car has no tag

        self.assertEqual(kiaee['brand'], 'Vehicle Brand: KIA')
        self.assertEqual(kiaee['turbo'], 'Car Turbo: No')
        self.assertEqual(kiaee.getTag(), 'Vehicle Tag')  # Car has no tag
        self.assertEqual(kiaee.tag, 'Vehicle Tag')  # Car has no tag
        self.assertEqual(kiaee._tag, 'Vehicle Tag')  # Car has no tag

        self.assertEqual(myKiaee['brand'], 'My Vehicle Brand: KIA')
        self.assertEqual(myKiaee['turbo'], 'Car Turbo: No')
        self.assertEqual(myKiaee.getTag(), 'MyVehicle Tag')  # Car has no tag
        self.assertEqual(myKiaee.tag, 'MyVehicle Tag')  # Car has no tag
        self.assertEqual(myKiaee._tag, 'MyVehicle Tag')  # Car has no tag

        self.assertEqual(lionee['art'], 'Animal Art: Lion')
        self.assertEqual(lionee['brand'], 'Vehicle Brand: Nature')
        self.assertEqual(lionee['turbo'], True)
        self.assertEqual(lionee['pedals'], 'Twin Turbo')
        self.assertEqual(lionee.getTag(), 'Animal Tag')  # Car has no tag
        self.assertEqual(lionee.tag, 'Animal Tag')  # Car has no tag
        self.assertEqual(lionee._tag, 'Animal Tag')  # Car has no tag

    def testOnNewClass(self):

        class A(Leaf):
            staticA = None

            @staticmethod
            def onNewClass(mixin):
                mixin.staticA = A

        class B(Leaf):
            staticB = None

            @staticmethod
            def onNewClass(mixin):
                mixin.staticB = B

        AB = As(A, B)

        self.assertEqual(A, AB.staticA)
        self.assertEqual(B, AB.staticB)

    def test_legacy(self):

        class Identity(Leaf):
            pass

        class XGAs(Leaf):
            columnSpecs = {
                'xG': {
                    'transformer': Helpers.argStripper(float, 1)
                }
            }

        class ProtoXGAs(Leaf):

            prototypes = [Identity, XGAs]

            columnSpecs = {
                'xG': {
                    'transformer': Helpers.argStripper(float, 1)
                }
            }

        m = {
            'a': 1,
            'b': 2,
            'c': 3,
        }
        m = As(Identity)(m)
        m['c'] = 33
        m['d'] = 44
        assert m['c'] == 33
        assert m['d'] == 44

        # iterate
        m = {
            'a': 1,
            'b': 2,
            'c': 3,
        }
        for key, val in Helpers.iterate(m):
            assert m[key] == val

        # Level 1 acces
        ps = As(Identity)({'xG': '1.1', 'name': 'test'})
        self.assertEqual(ps['xG'], '1.1')
        self.assertNotEqual(ps['xG'], float('1.1'))
        self.assertEqual(ps['name'], str('test'))

        ps = As(Identity, XGAs, classBlacklist=[XGAs])(
            {'xG': '1.1', 'name': 'test'})
        self.assertEqual(ps['xG'], '1.1')
        self.assertNotEqual(ps['xG'], float('1.1'))
        self.assertEqual(ps['name'], str('test'))

        ps = As(XGAs)({'xG': '1.1', 'name': 'test'})
        self.assertNotEqual(ps['xG'], '1.1')
        self.assertEqual(ps['xG'], float('1.1'))
        self.assertEqual(ps['name'], str('test'))

        ps = As(ProtoXGAs)({'xG': '1.1', 'name': 'test'})
        self.assertNotEqual(ps['xG'], '1.1')
        self.assertEqual(ps['xG'], float('1.1'))
        self.assertEqual(ps['name'], str('test'))


if __name__ == '__main__':
    unittest.main()
