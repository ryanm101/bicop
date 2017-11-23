from unittest import TestCase
from bicop.utils import same_type
from bicop.utils import merge


class Base(object):
    pass


class Child(Base):
    pass


class SameTypeTests(TestCase):
    def testTwoStrings(self):
        self.assertEqual(same_type('', ''), True)

    def testTwoDifferentTypes(self):
        self.assertEqual(same_type('', 1), False)

    def testSubClass(self):
        self.assertEqual(same_type(Base, Child), True)
        self.assertEqual(same_type(Child, Base), True)


class MergeTests(TestCase):
    def testMergingDifferentThings(self):
        self.assertRaises(ValueError, merge, dict(), '')

    def testMergeToSelf(self):
        one = dict(one=1)
        original = one.copy()
        merge(one, one)
        self.assertEqual(one, original)

    def testVarEntryOverlapping(self):
        one = dict(one=1)
        two = dict(two=2)
        merge(one, two)
        self.assertEqual(one, dict(one=1, two=2))
        self.assertEqual(two, dict(two=2))

    def testListEntryOverlapping(self):
        one = dict(one=1)
        two = dict(two=[1, 2, 3])
        merge(one, two)
        self.assertEqual(one, dict(one=1, two=[1, 2, 3]))
        self.assertEqual(two, dict(two=[1, 2, 3]))
        self.failUnless(one['two'] is two['two'])

    def testOverrideEntry(self):
        one = dict(one=1)
        two = dict(one=2)
        merge(one, two, True)
        self.assertEqual(one, dict(one=2))
        self.assertEqual(two, dict(one=2))

    def testOverrideList(self):
        one = dict(one=[1, 2])
        two = dict(one=[3, 4])
        merge(one, two, True)
        self.assertEqual(one, dict(one=[3, 4]))

    def testOverrideTypeMismatch(self):
        one = dict(one=1)
        two = dict(one=[3, 4])
        self.assertRaises(ValueError, merge, one, two, True)

    def testOverrideAllowedTypeMismatch(self):
        one = dict(one=1)
        two = dict(one=[3, 4])
        merge(one, two, True, False)
        self.assertEqual(one, dict(one=[3, 4]))

    def testDeepMerge(self):
        one = dict(people=dict(john='male'))
        two = dict(people=dict(jane='female'))
        merge(one, two)
        self.assertEqual(one, dict(people=dict(john='male', jane='female')))
