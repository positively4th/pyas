import unittest

from src.pyas_v3 import As
from src.pyas_v3 import Leaf
from src.pyas_v3 import Helpers
from src.pyas_v3 import T
from src.pyas_v3 import PyasException


class TestT(unittest.TestCase):

    def test_virtual(self):

        class ConstantMap(Leaf):

            prototypes = []

            columnSpecs = {
                'const1': {
                    'transformer': T.virtual(lambda *_: 'One')
                },
                'const2': {
                    'transformer': T.virtual(lambda *_: 'Two')
                },
                'const3': {
                    'transformer': T.virtual(lambda *_: 'Three')
                },
            }

        constantMap = {
            'const2': 'Two',
            'const3': 'Three',
        }

        constantMapee = As(ConstantMap)(constantMap)

        self.assertEquals('One', constantMapee['const1'])

        with self.assertRaises(Exception) as context:
            constantMapee['const1'] = '1'
        self.assertEquals(PyasException, context.exception.__class__)
        self.assertEquals(
            'Virtual column const1 cannot be assigned.', str(context.exception))

        with self.assertRaises(Exception) as context:
            constantMapee['const2']
        self.assertEquals(PyasException, context.exception.__class__)
        self.assertEquals(
            'Virtual column const2 has value.', str(context.exception))

        with self.assertRaises(Exception) as context:
            constantMapee['const2'] = '2'
        self.assertEquals(PyasException, context.exception.__class__)
        self.assertEquals(
            'Virtual column const2 cannot be assigned.', str(context.exception))

        with self.assertRaises(Exception) as context:
            constantMapee['const3']
        self.assertEquals(PyasException, context.exception.__class__)
        self.assertEquals(
            'Virtual column const3 has value.', str(context.exception))

        with self.assertRaises(Exception) as context:
            constantMapee['const3'] = '3'
        self.assertEquals(PyasException, context.exception.__class__)
        self.assertEquals(
            'Virtual column const3 cannot be assigned.', str(context.exception))

    def test_constantNotEmpty(self):

        class ConstantMap(Leaf):

            prototypes = []

            columnSpecs = {
                'const1': {
                    'transformer': T.constantNotEmpty()
                },
                'const2': {
                    'transformer': T.constantNotEmpty()
                },
            }

        constantMap = {
            'const1': 'One',
        }

        constantMapee = As(ConstantMap)(constantMap)

        self.assertEquals('One', constantMapee['const1'])
        constantMapee['const1'] = 'One'
        self.assertEquals('One', constantMapee['const1'])

        with self.assertRaises(Exception) as context:
            constantMapee['const1'] = '1'
        self.assertEquals(PyasException, context.exception.__class__)
        self.assertEquals(
            'Constant column const1 can not be changed.', str(context.exception))

        with self.assertRaises(Exception) as context:
            constantMapee['const2']
        self.assertEquals(PyasException, context.exception.__class__)
        self.assertEquals(
            'Missing column const2.', str(context.exception))

        with self.assertRaises(Exception) as context:
            constantMapee['const2'] = '2'
        self.assertEquals(PyasException, context.exception.__class__)
        self.assertEquals(
            'Missing column const2.', str(context.exception))

    def test_constant(self):

        class ConstantMap(Leaf):

            prototypes = []

            columnSpecs = {
                'const1': {
                    'transformer': T.constant('One')
                },
                'const2': {
                    'transformer': T.constant('Two')
                },
                'const3': {
                    'transformer': T.constant('Three')
                },
            }

        constantMap = {
            'const1': 'One',
        }

        constantMapee = As(ConstantMap)(constantMap)

        self.assertEquals('One', constantMapee['const1'])
        constantMapee['const1'] = 'One'
        self.assertEquals('One', constantMapee['const1'])

        with self.assertRaises(Exception) as context:
            constantMapee['const1'] = '1'
        self.assertEquals(PyasException, context.exception.__class__)
        self.assertEquals(
            'Constant column const1 can not be changed.', str(context.exception))

        with self.assertRaises(Exception) as context:
            constantMapee['const2'] = '2'
        self.assertEquals(PyasException, context.exception.__class__)
        self.assertEquals(
            'Constant column const2 can not be changed.', str(context.exception))

        self.assertEquals('Two', constantMapee['const2'])

        with self.assertRaises(Exception) as context:
            constantMapee['const3'] = '3'
        self.assertEquals(PyasException, context.exception.__class__)
        self.assertEquals(
            'Constant column const3 can not be changed.', str(context.exception))

        constantMapee['const3'] = 'Three'
        self.assertEquals('Three', constantMapee['const3'])


if __name__ == '__main__':
    unittest.main()
