#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from pyparsecom.datatypes import ParseObject


class ParseObjectTest(unittest.TestCase):

    def setUp(self):
        pass

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