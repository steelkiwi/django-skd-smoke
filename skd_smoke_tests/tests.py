# -*- coding: utf-8 -*-
from __future__ import unicode_literals
import types
from unittest import TestCase

from skd_smoke.__init__ import generate_test_method, prepare_test_name, \
    prepare_configuration, generate_fail_test_method, prepare_test_method_doc


class SmokeGeneratorTestCase(TestCase):

    def test_prepare_configuration(self):
        test = prepare_configuration([(u'a', 200, u'GET'),
                                      (u'b', 200, u'GET')])
        self.assertIsNotNone(test)
        self.assertEquals(
            test, [(u'a', 200, u'GET', None), (u'b', 200, u'GET', None)])

    def test_generate_fail_test_method(self):
        test = generate_fail_test_method('test')
        self.assertIsNotNone(test)
        self.assertEquals(type(test), types.FunctionType)
        self.assertEquals(test.__name__, 'fail_method')

    def test_generate_test_method(self):
        test = generate_test_method('urlname', 200, method='GET', data=None)
        self.assertIsNotNone(test)
        self.assertEquals(type(test), types.FunctionType)
        self.assertEquals(test.__name__, 'new_test_method')

    def test_prepare_test_name(self):
        test = prepare_test_name('urlname', 'GET', 200)
        name = test[0:test.rfind('_')]
        self.assertEqual(name, 'test_smoke_urlname_get_200')

    def test_prepare_test_method_doc(self):
        test = prepare_test_method_doc('GET', 'urlname', 200, 'status_text',
                                       None)
        self.assertIsNotNone(test)
        self.assertEquals(test, 'GET urlname 200 "status_text" None')
