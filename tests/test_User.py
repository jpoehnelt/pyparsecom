#!/usr/bin/env python
# -*- coding: utf-8 -*-
import unittest
from pyparsecom.user import User
from pyparsecom.objects import Parse
from pyparsecom.exceptions import ParseError
import uuid


class UserTest(unittest.TestCase):
    def setUp(self):
        Parse.initialize('w32obnqOXh5n61OTuXIAbRZRj73oyEWCDuMBOQQu',
                         'ZjCmqLRivFF16Ei8PV044XU0VgoqNL34wuvI4NQ7')

    def tearDown(self):
        pass

    def test_login(self):
        username = str(uuid.uuid4())
        user = User.signup(username, 'password')
        user2 = User.login(username, 'password')
        self.assertEqual(username, user2.username)
        self.assertEqual(len(user2._dirty_keys), 0)

    def test_signup(self):
        username = str(uuid.uuid4())
        user = User.signup(username, 'password')
        self.assertTrue(hasattr(user, 'sessionToken'))
        self.assertEqual(len(user._dirty_keys), 0)

    def test_become(self):
        username = str(uuid.uuid4())
        user = User.signup(username, 'password')

        user2 = User.become(user.sessionToken)
        self.assertEqual(username, user2.username)
        self.assertEqual(len(user2._dirty_keys), 0)

    def test_delete_of_user(self):
        username = str(uuid.uuid4())
        user = User.signup(username, 'password')
        user.delete()
        self.assertRaises(ParseError, User.login, username, 'password')

    def test_error_is_raised_on_invalid_login(self):
        username = str(uuid.uuid4())
        self.assertRaises(ParseError, User.login, username, 'password')

    def test_user_as_pointer(self):
        username = str(uuid.uuid4())
        user = User.signup(username, 'password')
        pointer = user.to_pointer()
        pointer_data = pointer._convert_from_native_to_parse()
        self.assertEqual(pointer_data['className'], '_User')
        self.assertEqual(pointer_data['__type'], 'Pointer')
        self.assertEqual(pointer_data['objectId'], user.objectId)
