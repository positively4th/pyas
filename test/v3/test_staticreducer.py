import unittest

from src.pyas_v3 import As
from src.pyas_v3 import Leaf
from src.pyas_v3 import Helpers
from src.pyas_v3 import T
from src.pyas_v3 import PyasException
from src.pyas_v3 import Reducers


theAStr0 = 'A'
theATuple0 = ('A', 'X')
theAList0 = ['A', 'X']
theASet0 = set(['A', 'X'])
theADict0 = {'A': 'A', 'X': 'XA', 'Y': 'Y'}

theBStr0 = 'B'
theBTuple0 = ('B', 'X')
theBList0 = ['B', 'X']
theBSet0 = set(['B', 'X'])
theBDict0 = {'B': 'B', 'X': 'XB', 'Y': 'Y'}


class TestStaticReducer(unittest.TestCase):

    @staticmethod
    def createAAndB():
        class A(Leaf):

            prototypes = []

            theStr = str(theAStr0)
            theTuple = tuple(theATuple0)
            theList = list(theAList0)
            theSet = theASet0
            theDict = dict(theADict0)

        class B(Leaf):

            prototypes = []

            theStr = str(theBStr0)
            theTuple = tuple(theBTuple0)
            theList = theBList0
            theSet = theBSet0
            theDict = dict(theBDict0)

        return A, B

    def test_noReducer(self):

        A, B = self.createAAndB()
        AB = As(A, B)

        abee = As(AB)({})

        self.assertEqual(theAStr0, A.theStr)
        self.assertEqual(theADict0, A.theDict)
        self.assertEqual(theBStr0, B.theStr)
        self.assertEqual(theBDict0, B.theDict)
        self.assertEqual(theAStr0, AB.theStr)
        self.assertEqual(theADict0, AB.theDict)

        A.theStr = theAStr1 = 'AA'
        A.theDict = theADict1 = {**theADict0, **{'A': 'AA'}}

        self.assertEqual(theAStr1, A.theStr)
        self.assertEqual(theADict1, A.theDict)
        self.assertEqual(theBStr0, B.theStr)
        self.assertEqual(theBDict0, B.theDict)
        self.assertEqual(theAStr1, AB.theStr)
        self.assertEqual(theADict1, AB.theDict)

        B.theStr = theBStr1 = 'BB'
        B.theDict = theBDict1 = {**theADict0, **{'B': 'BB'}}
        self.assertEqual(theAStr1, A.theStr)
        self.assertEqual(theADict1, A.theDict)
        self.assertEqual(theBStr1, B.theStr)
        self.assertEqual(theBDict1, B.theDict)
        self.assertEqual(theAStr1, AB.theStr)
        self.assertEqual(theAStr1, abee.theStr)
        self.assertEqual(theADict1, AB.theDict)

    def test_clone_As(self):

        A, B = self.createAAndB()

        AB = As(A, B, staticReducers={
            'theStr': Reducers.clone,
            'theDict': Reducers.clone,
        })

        abee = As(AB)({})

        self.assertEqual(theAStr0, A.theStr)
        self.assertEqual(theADict0, A.theDict)
        self.assertEqual(theBStr0, B.theStr)
        self.assertEqual(theBDict0, B.theDict)
        self.assertEqual(theAStr0, AB.theStr)
        self.assertEqual(theADict0, AB.theDict)

        A.theStr = theAStr1 = 'AA'
        A.theDict = theADict1 = {**theADict0, **{'A': 'AA'}}

        self.assertEqual(theAStr1, A.theStr)
        self.assertEqual(theADict1, A.theDict)
        self.assertEqual(theBStr0, B.theStr)
        self.assertEqual(theBDict0, B.theDict)
        self.assertEqual(theAStr0, AB.theStr)
        self.assertEqual(theADict0, AB.theDict)

        B.theStr = theBStr1 = 'BB'
        B.theDict = theBDict1 = {**theADict0, **{'B': 'BB'}}
        self.assertEqual(theAStr1, A.theStr)
        self.assertEqual(theADict1, A.theDict)
        self.assertEqual(theBStr1, B.theStr)
        self.assertEqual(theBDict1, B.theDict)
        self.assertEqual(theAStr0, AB.theStr)
        self.assertEqual(theADict0, AB.theDict)

        AB.theStr = theABStr1 = 'AB'
        AB.theDict = theABDict1 = {**theADict0, **{'AB': 'ABAV'}}
        self.assertEqual(theAStr1, A.theStr)
        self.assertEqual(theADict1, A.theDict)
        self.assertEqual(theBStr1, B.theStr)
        self.assertEqual(theBDict1, B.theDict)
        self.assertEqual(theABStr1, AB.theStr)
        self.assertEqual(theABDict1, AB.theDict)

    def test_clone_B(self):

        A, B = self.createAAndB()
        B.staticReducers = {
            'theStr': Reducers.clone,
            'theDict': Reducers.clone,
        }

        AB = As(A, B)

        abee = As(AB)({})

        self.assertEqual(theAStr0, A.theStr)
        self.assertEqual(theADict0, A.theDict)
        self.assertEqual(theBStr0, B.theStr)
        self.assertEqual(theBDict0, B.theDict)
        self.assertEqual(theAStr0, AB.theStr)
        self.assertEqual(theADict0, AB.theDict)

        A.theStr = theAStr1 = 'AA'
        A.theDict = theADict1 = {**theADict0, **{'A': 'AA'}}

        self.assertEqual(theAStr1, A.theStr)
        self.assertEqual(theADict1, A.theDict)
        self.assertEqual(theBStr0, B.theStr)
        self.assertEqual(theBDict0, B.theDict)
        self.assertEqual(theAStr0, AB.theStr)
        self.assertEqual(theADict0, AB.theDict)

        B.theStr = theBStr1 = 'BB'
        B.theDict = theBDict1 = {**theADict0, **{'B': 'BB'}}
        self.assertEqual(theAStr1, A.theStr)
        self.assertEqual(theADict1, A.theDict)
        self.assertEqual(theBStr1, B.theStr)
        self.assertEqual(theBDict1, B.theDict)
        self.assertEqual(theAStr0, AB.theStr)
        self.assertEqual(theADict0, AB.theDict)

        AB.theStr = theABStr1 = 'AB'
        AB.theDict = theABDict1 = {**theADict0, **{'AB': 'ABAV'}}
        self.assertEqual(theAStr1, A.theStr)
        self.assertEqual(theADict1, A.theDict)
        self.assertEqual(theBStr1, B.theStr)
        self.assertEqual(theBDict1, B.theDict)
        self.assertEqual(theABStr1, AB.theStr)
        self.assertEqual(theABDict1, AB.theDict)

    def test_parentExtends_As(self):

        A, B = self.createAAndB()

        AB = As(A, B, staticReducers={
            'theStr': Reducers.parentExtends,
            'theTuple': Reducers.parentExtends,
            'theList': Reducers.parentExtends,
            'theSet': Reducers.parentExtends,
            'theDict': Reducers.parentExtends,
        })

        abee = As(AB)({})

        self.assertEqual(theAStr0, A.theStr)
        self.assertEqual(theATuple0, A.theTuple)
        self.assertEqual(theAList0, A.theList)
        self.assertEqual(theASet0, A.theSet)
        self.assertEqual(theADict0, A.theDict)

        self.assertEqual(theBStr0, B.theStr)
        self.assertEqual(theBTuple0, B.theTuple)
        self.assertEqual(theBList0, B.theList)
        self.assertEqual(theBSet0, B.theSet)
        self.assertEqual(theBDict0, B.theDict)

        self.assertEqual(theBStr0 + theAStr0, AB.theStr)
        self.assertEqual(theBTuple0 + theATuple0, AB.theTuple)
        self.assertEqual(theBList0 + theAList0, AB.theList)
        self.assertEqual(theBSet0.union(theASet0), AB.theSet)
        self.assertEqual({**theBDict0, **theADict0}, AB.theDict)


if __name__ == '__main__':
    unittest.main()
