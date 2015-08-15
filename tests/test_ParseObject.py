#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from pyparsecom.core import Parse
from pyparsecom.datatypes import ParseObject


class ParseObjectTest(unittest.TestCase):
    def setUp(self):
        Parse.initialize('w32obnqOXh5n61OTuXIAbRZRj73oyEWCDuMBOQQu',
                         'ZjCmqLRivFF16Ei8PV044XU0VgoqNL34wuvI4NQ7')

    def tearDown(self):
        pass

    def test_object_extend(self):
        Custom = ParseObject.extend('Custom')
        c = Custom()
        self.assertEqual(type(c).__name__, 'Custom')

    def test_attributes(self):
        Custom = ParseObject.extend('Custom')
        c = Custom()
        c.a = 1
        self.assertEqual(c.a, 1)

        d = Custom(name='something')
        self.assertEqual(d.name, 'something')

    def test_create_object(self):
        City = ParseObject.extend('City')

        ny = City(name='New York')
        ny.save()

        self.assertIsNotNone(ny.objectId)
        self.assertIsNotNone(ny.createdAt)

    def test_fetch(self):
        City = ParseObject.extend('City')

        ny = City(name='New York')
        ny.save()

        ny.fetch()
        self.assertIsNotNone(ny.objectId)
        self.assertIsNotNone(ny.createdAt)
        self.assertIsNotNone(ny.updatedAt)

    def test_get(self):
        City = ParseObject.extend('City')

        ny = City(name='New York')
        ny.save()

        ny2 = City.get(ny.objectId)
        self.assertEqual(ny.objectId, ny2.objectId)
