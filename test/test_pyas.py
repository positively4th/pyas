import unittest
import re

from src.pyas import As
from src.pyas import Helpers

class TestAs(unittest.TestCase):

    def test_cache(self):

        class Testee(As):

            initCounter = 0
            
            def __init__(self, row, *args, **kwargs):
                Testee.initCounter += 1
                super().__init__(row, *args, **kwargs)
                    

        row1 = {'a':1 , 'b':10}
        row2 = {'a':2 , 'b':20}
        row23 = {'a':2 , 'b':20}

        tm11 = Testee.create(row1)
        tm12 = Testee.create(row1)
        tm21 = Testee.create(row2)
        tm22 = Testee.create(row2)
        tm23 = Testee.create(row23)

        self.assertEqual(Testee.initCounter, 3)

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
       
        self.assertRaises(AssertionError, Testee, row1)
        
    def testLegacy(self):
        #__seitem__

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
        columnSpecs = {
            'xG': {
                'T': As.argStripper(float, 1)
            }
        }
        #ps = As.create({'xG': '1.1', 'name': 'test'}, transformers={'xG': As.argStripper(float, 1)})
        ps = As.create({'xG': '1.1', 'name': 'test'}, columnSpecs)
        #assert ps.xG == float('1.1')
        assert ps['xG'] != '1.1'
        assert ps['xG'] == float('1.1')
        assert ps['name'] == str('test')

        #Level 1 acces
        ps = As.create({'xG': '1.1', 'name': 'test'}, columnSpecs={
            'xG': {
                'T': As.argStripper(float, 1)
            }})
        #assert ps.xG == float('1.1')
        assert ps['xG'] != '1.1'
        assert ps['xG'] == float('1.1')
        assert ps['name'] == str('test')

        #Level 3 acces
        ps = As.create({'a': '1', 'mat': [[i * j for j in range(0,3)] for i in range(0,3)]})
        assert ps['mat', 0, 0] == 0
        assert ps['mat', 0, 1] == 0
        assert ps['mat', 0, 2] == 0
        assert ps['mat', 1, 0] == 0
        assert ps['mat', 1, 1] == 1
        assert ps['mat', 1, 2] == 2
        assert ps['mat', 2, 0] == 0
        assert ps['mat', 2, 1] == 2
        assert ps['mat', 2, 2] == 4

        #Match
        class Match(As):
            columnSpecs = {
                'xG': {
                    'T': As.argStripper(float, 1)
                }
        }
                        
        ps = Match.create({'xG': '1.1', 'name': 'test'})
        assert ps.match({
            'name': 'test',
        }, compile=True)

        assert not ps.match({
            'name': 'xtest',
        }, compile=True)

        assert ps.match({
            'name': re.compile('test'),
            'xG': re.compile('1[.]1'),
        }, compile=True)

        assert not ps.match({
            'name': re.compile('testx'),
            'xG': re.compile('1[.]1'),
        }, compile=True)

        assert not ps.match({
            'name': re.compile('test'),
            'xG': re.compile('2[.]1'),
        }, compile=True)


if __name__ == '__main__':
    unittest.main()

    
