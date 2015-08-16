#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from pyparsecom.types import GeoPoint


class ParseObjectTest(unittest.TestCase):
    def setUp(self):
        pass

    def tearDown(self):
        pass

    def test_equal(self):
        geo = GeoPoint(latitude=40.0, longitude=-30)
        geo2 = GeoPoint(latitude=40.0, longitude=-30)
        geo3 = GeoPoint(latitude=80.0, longitude=-70)

        self.assertEqual(geo, geo2)
        self.assertNotEqual(geo, geo3)



