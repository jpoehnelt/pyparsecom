#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from pyparsecom.query import Query
from pyparsecom.objects import ParseObject
from tests import init_parse


class QueryTest(unittest.TestCase):
    def setUp(self):
        init_parse()

    def tearDown(self):
        pass

    def create_cities(self):
        class City(ParseObject):
            pass

        ny = City(name='New York')
        sf = City(name='San Francisco', country='United States')
        ny.save()
        sf.save()

    def test_simple_fetch(self):
        class City(ParseObject):
            pass

        ny = City(name='New York')
        ny.save()
        query = Query('City')

        cities = query.fetch()
        for city in cities:
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
        ny2 = Query('City').get(ny.objectId)

        self.assertTrue(isinstance(ny2, City))
        self.assertEqual(ny.objectId, ny2.objectId)

    def test_where(self):
        class City(ParseObject):
            pass

        name = 'New York'

        ny = City(name=name)
        sf = City(name='San Francisco')
        ny.save()
        sf.save()

        query = Query('City').equal_to('name', name)
        cities = query.fetch()

        self.assertTrue(len(cities) > 0)

        for city in cities:
            self.assertEqual(city.name, name)

    def test_keys(self):
        class City(ParseObject):
            pass

        name = 'New York'

        ny = City(name=name)
        sf = City(name='San Francisco', country='United States')
        ny.save()
        sf.save()

        query = Query('City').keys(['country'])
        cities = query.fetch()

        self.assertTrue(len(cities) > 0)

        for city in cities:
            self.assertRaises(AttributeError, getattr, city, 'name')
            self.assertFalse(city._is_loaded)

    def test_limit(self):
        class City(ParseObject):
            pass

        name = 'New York'

        ny = City(name=name)
        sf = City(name='San Francisco', country='United States')
        ny.save()
        sf.save()

        query = Query('City')
        cities = query.limit(1).fetch()

        self.assertTrue(len(cities) == 1)

        query = Query('City')
        cities = query.limit(1).fetch()

        self.assertTrue(len(cities) == 1)

    def test_exists(self):
        self.create_cities()
        query = Query('City')
        query = query.exists('country')
        cities = query.fetch()

        self.assertTrue(len(cities) > 0)
        for city in cities:
            self.assertTrue(hasattr(city, 'country'))

    def test_does_not_exist(self):
        self.create_cities()
        query = Query('City')
        query = query.does_not_exist('country')
        cities = query.fetch()

        self.assertTrue(len(cities) > 0)
        for city in cities:
            self.assertFalse(hasattr(city, 'country'))



