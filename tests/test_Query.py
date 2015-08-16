#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from pyparsecom.core import Parse
from pyparsecom.objects import ParseObject


class QueryTest(unittest.TestCase):
    def setUp(self):
        Parse.initialize('w32obnqOXh5n61OTuXIAbRZRj73oyEWCDuMBOQQu',
                         'ZjCmqLRivFF16Ei8PV044XU0VgoqNL34wuvI4NQ7')

    def tearDown(self):
        pass

    def test_simple_fetch(self):
        class City(ParseObject):
            pass

        ny = City(name='New York')
        ny.save()
        query = Parse.Query('City')

        cities = query.fetch()
        for city in cities:
            print(city.__dict__)
            self.assertTrue(isinstance(city, City))
            self.assertTrue(city._is_loaded)
            self.assertTrue(hasattr(city, 'objectId'))
            for k, v in city.__dict__.items():
                self.assertFalse(isinstance(v, dict))

    def test_get(self):
        class City(ParseObject):
            pass

        ny = City(name='New York')
        ny.save()
        ny2 = Parse.Query('City').get(ny.objectId)

        self.assertTrue(isinstance(ny2, City))
        self.assertEqual(ny.objectId, ny2.objectId)