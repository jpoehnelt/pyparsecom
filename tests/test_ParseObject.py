#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from pyparsecom.core import Parse
from pyparsecom.objects import ParseObject, ComplexTypeMeta


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

    def test_get(self):
        class City(ParseObject):
            pass

        ny = City(name='New York')
        ny.save()

        ny2 = City.get(ny.objectId)
        self.assertEqual(ny.objectId, ny2.objectId)

    def test_complex_type_as_attribute_has_correct_class(self):
        class City(ParseObject):
            pass

        ny = City(name='New York')
        ny.location = {
            "__type": "GeoPoint",
            "latitude": 40.0,
            "longitude": -30.0
        }

        ny.save()
        ny.fetch()

        self.assertEqual(ny.location.__name__, 'GeoPoint')

