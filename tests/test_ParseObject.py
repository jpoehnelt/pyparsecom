#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from pyparsecom.core import Parse
from pyparsecom.objects import ParseObject, ComplexTypeMeta
from pyparsecom.types import GeoPoint
from pyparsecom.exceptions import ParseError


class ParseObjectTest(unittest.TestCase):
    def setUp(self):
        Parse.initialize('w32obnqOXh5n61OTuXIAbRZRj73oyEWCDuMBOQQu',
                         'ZjCmqLRivFF16Ei8PV044XU0VgoqNL34wuvI4NQ7')

    def tearDown(self):
        pass

    def test_object_class_register(self):
        class Custom(ParseObject):
            pass

        class MoreCustom(Custom):
            pass

        self.assertTrue('Custom' in ComplexTypeMeta.register)
        self.assertTrue('MoreCustom' in ComplexTypeMeta.register)

    def test_object_attributes(self):
        class Custom(ParseObject):
            pass

        c = Custom()
        c.a = 1
        self.assertEqual(c.a, 1)

        d = Custom(name='something')
        self.assertEqual(d.name, 'something')

    def test_create_object(self):
        class City(ParseObject):
            pass

        ny = City(name='New York')
        ny.save()

        self.assertNotEqual(ny.objectId, None)
        self.assertNotEqual(ny.createdAt, None)

    def test_fetch(self):
        class City(ParseObject):
            pass

        ny = City(name='New York')
        ny.save()

        ny.fetch()
        self.assertNotEqual(ny.objectId, None)
        self.assertNotEqual(ny.createdAt, None)
        self.assertNotEqual(ny.updatedAt, None)

    def test_complex_type_as_attribute_has_correct_class(self):
        class City(ParseObject):
            pass

        ny = City(name='New York')

        geo = GeoPoint(latitude=40.0, longitude=-30)

        ny.location = geo

        ny.save()
        ny.fetch()

        self.assertEqual(ny.location.__name__, 'GeoPoint')

        ny2 = City(objectId=ny.objectId)
        ny2.fetch()

        self.assertEqual(ny2.location.__name__, 'GeoPoint')


    def test_to_pointer_and_back(self):
        class City(ParseObject):
            pass

        ny = City(name='New York')
        pointer = ny.to_pointer()
        ny2 = pointer.load()
        ny2.fetch()

        self.assertEqual(ny.name, ny2.name)

    def test_is_loaded(self):
        class City(ParseObject):
            pass

        ny = City(name='New York')
        self.assertFalse(ny._is_loaded)
        ny.save()
        self.assertFalse(ny._is_loaded)
        ny.fetch()
        self.assertTrue(ny._is_loaded)

        pointer = ny.to_pointer()
        ny2 = pointer.load()
        self.assertTrue(ny._is_loaded)

    def test_dirty_keys(self):
        class City(ParseObject):
            pass

        ny = City(name='New York')
        self.assertTrue('name' in ny._dirty_keys)
        ny.save()
        self.assertFalse('name' in ny._dirty_keys)

    def test_dirty_keys_with_complex_type(self):
        class City(ParseObject):
            pass

        ny = City(name='New York')
        geo = GeoPoint(latitude=40.0, longitude=-30)
        geo2 = GeoPoint(latitude=40.0, longitude=-30)

        ny.location = geo
        self.assertTrue(ny in geo._parents)
        self.assertTrue('location' in ny._dirty_keys)

        ny.save()
        self.assertFalse('location' in ny._dirty_keys)

        # try changing attribute of complex type
        geo.latitude = 0.00
        self.assertTrue('location' in ny._dirty_keys)

        ny.save()
        self.assertFalse('location' in ny._dirty_keys)

        # try deleting attribute of complex type
        geo.test = 1
        ny._dirty_keys.clear()
        del geo.test
        self.assertTrue('location' in ny._dirty_keys)

        # try replacing reference to complex type
        ny.location = geo2
        ny.save()
        self.assertTrue(ny in geo2._parents)
        self.assertFalse(ny in geo._parents)
        geo.latitude = 0.00
        self.assertFalse('location' in ny._dirty_keys)

        # try deleting reference to complex type
        del ny.location
        self.assertFalse(ny in geo2._parents)
        self.assertFalse(ny in geo2._parents)

        # ParseObject attribute of ParseObject does not carry dirty to parent since it uses pointer
        sf = City(name='San Francisco')
        ny.sibling = sf
        self.assertTrue('sibling' in ny._dirty_keys)
        ny._dirty_keys.clear()
        sf.name = 'San Jose'
        self.assertTrue('name' in sf._dirty_keys)
        self.assertFalse('sibling' in ny._dirty_keys)

    def test_delete_of_object(self):
        class City(ParseObject):
            pass

        ny = City(name='New York')
        ny.save()
        ny.delete()
        self.assertRaises(ParseError, ny.fetch)