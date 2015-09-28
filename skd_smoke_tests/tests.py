# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import types
from unittest import TestCase
from mock import Mock, MagicMock, patch
from skd_smoke import generate_test_method, prepare_test_name, \
    prepare_configuration, generate_fail_test_method, prepare_test_method_doc,\
    SmokeTestCase, EMPTY_TEST_CONFIGURATION_MSG, \
    INCORRECT_TEST_CONFIGURATION_MSG, IMPROPERLY_BUILT_CONFIGURATION_MSG


class SmokeGeneratorTestCase(TestCase):

    def test_prepare_configuration(self):
        test = prepare_configuration([('a', 200, 'GET'),
                                      ('b', 200, 'GET')])
        self.assertIsNotNone(test)
        self.assertEquals(
            test, [('a', 200, 'GET', None), ('b', 200, 'GET', None)])

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

    def test_prepare_test_name_with_just_urlname(self):
        test = prepare_test_name('urlname', 'GET', 200)
        name = test[0:test.rfind('_')]
        self.assertEqual(name, 'test_smoke_urlname_get_200')

    def test_prepare_test_name_with_namespace_urlname(self):
        test = prepare_test_name('namespace:urlname', 'GET', 200)
        name = test[0:test.rfind('_')]
        self.assertEqual(name, 'test_smoke_namespace_urlname_get_200')

    def test_prepare_test_name_with_plain_url(self):
        test = prepare_test_name('/enclosed/url/', 'GET', 200)
        name = test[0:test.rfind('_')]
        self.assertEqual(name, 'test_smoke_enclosed_url_get_200')

    def test_prepare_test_method_doc(self):
        test = prepare_test_method_doc('GET', 'urlname', 200, 'status_text',
                                       None)
        self.assertIsNotNone(test)
        self.assertEquals(test, 'GET urlname 200 "status_text" None')


class SmokeTestCaseTesting(TestCase):

    def check_if_class_contains_test_methods(self, cls, prefix='test_smoke'):

        for attr in cls.__dict__:
            if attr.startswith(prefix):
                return True

        return False

    def check_if_class_contains_fail_test_method(self, cls):
        return hasattr(cls, getattr(cls, 'FAIL_METHOD_NAME'))

    def mock_and_check_fail_test_method(self, cls, msg):
        method_name = getattr(cls, 'FAIL_METHOD_NAME')
        fail_test_method = getattr(cls, method_name)

        mock = Mock(spec=cls)
        fail_test_method(mock)
        self.assertEqual(mock.fail.call_count, 1)
        self.assertIn(msg, mock.fail.call_args_list[0][0][0])

    def check_generated_test_method(self, cls, name, configuration, doc, url):
        # check existence
        self.assertTrue(hasattr(cls, name),
                        'There is no "%s" in %s but should be.' % (name, cls))

        test_method = getattr(cls, name)
        _, status_code, method, data = configuration
        method_lower = method.lower()

        # check __name__
        self.assertEqual(test_method.__name__, name)

        # check __doc__
        self.assertEqual(test_method.__doc__, doc)

        method_mock = MagicMock()
        method_mock.return_value = MagicMock(status_code=status_code)

        # check actual run
        client_mock = MagicMock(**{method_lower: method_mock})

        testcase_mock = Mock(spec=cls, client=client_mock)
        testcase_mock.assertEqual = Mock()
        test_method(testcase_mock)
        getattr(client_mock, method_lower).assert_called_once_with(
            url, data=data or {})
        testcase_mock.assertEqual.assert_called_once_with(
            status_code, status_code)

    def test_empty_configuration(self):
        EmptyConfig = type(
            str('BrokenConfig'), (SmokeTestCase,), {'TESTS_CONFIGURATION': ()})
        self.assertFalse(
            self.check_if_class_contains_test_methods(EmptyConfig),
            'TestCase contains generated test method but should not '
            '(test configuration is empty).'
        )
        self.assertTrue(
            self.check_if_class_contains_fail_test_method(EmptyConfig),
            'Generated TestCase should contain one fake test method to inform '
            'that its configuration is empty.'
        )

        self.mock_and_check_fail_test_method(
            EmptyConfig, EMPTY_TEST_CONFIGURATION_MSG)

    def test_configuration_in_wrong_type(self):
        BrokenConfig = type(str('BrokenConfig'), (SmokeTestCase,), {})
        self.assertFalse(
            self.check_if_class_contains_test_methods(BrokenConfig),
            'TestCase contains generated test method but should not '
            '(test configuration is broken).'
        )
        self.assertTrue(
            self.check_if_class_contains_fail_test_method(BrokenConfig),
            'Generated TestCase should contain one fake test method to inform '
            'that its configuration is broken.'
        )

        self.mock_and_check_fail_test_method(
            BrokenConfig, INCORRECT_TEST_CONFIGURATION_MSG)

    def test_configuration_built_incorrectly(self):
        conf = (
            ('a', 200),  # too few arguments
        )

        BrokenConfig = type(
            str('BrokenConfig'),
            (SmokeTestCase,),
            {'TESTS_CONFIGURATION': conf})
        self.assertFalse(
            self.check_if_class_contains_test_methods(BrokenConfig),
            'TestCase contains generated test method but should not '
            '(test configuration is broken).'
        )
        self.assertTrue(
            self.check_if_class_contains_fail_test_method(BrokenConfig),
            'Generated TestCase should contain one fake test method to inform '
            'that its configuration is broken.'
        )

        self.mock_and_check_fail_test_method(
            BrokenConfig, IMPROPERLY_BUILT_CONFIGURATION_MSG)

    def test_simple_correct_configuration(self):
        conf = (
            ('a', 200, 'GET', {}),
        )

        CorrectConfig = type(
            str('CorrectConfig'),
            (SmokeTestCase,),
            {'TESTS_CONFIGURATION': conf})
        self.assertTrue(
            self.check_if_class_contains_test_methods(CorrectConfig),
            'TestCase contains generated test method but should not '
            '(test configuration is broken).'
        )
        self.assertFalse(
            self.check_if_class_contains_fail_test_method(CorrectConfig),
            'Generated TestCase should not contain fail test method cause '
            'its configuration is correct.'
        )

    @patch('skd_smoke.uuid4')
    @patch('skd_smoke.resolve_url')
    def test_generated_test_methods(self, mock_django_resolve_url, mock_uuid4):
        conf = (
            ('/some_url/', 200, 'GET', {}),
            ('/comments/', 201, 'POST', {'message': 'new comment'}),
            ('namespace:url', 200, 'GET', {}),
            ('some_url2', 200, 'GET', {}),
        )

        expected_test_method_names = [
            'test_smoke_some_url_get_200_ffffffff',
            'test_smoke_comments_post_201_ffffffff',
            'test_smoke_namespace_url_get_200_ffffffff',
            'test_smoke_some_url2_get_200_ffffffff',
        ]

        expected_docs = [
            'GET /some_url/ 200 "OK" {}',
            'POST /comments/ 201 "CREATED" %r' % ({'message': 'new comment'},),
            'GET namespace:url 200 "OK" {}',
            'GET some_url2 200 "OK" {}',
        ]

        mock_django_resolve_url.return_value = url = '/url/'
        mock_uuid4.return_value = MagicMock(hex='ffffffff')

        CorrectConfig = type(
            str('CorrectConfig'),
            (SmokeTestCase,),
            {'TESTS_CONFIGURATION': conf})
        self.assertTrue(
            self.check_if_class_contains_test_methods(CorrectConfig),
            'TestCase contains generated test method but should not '
            '(test configuration is broken).'
        )
        self.assertFalse(
            self.check_if_class_contains_fail_test_method(CorrectConfig),
            'Generated TestCase should not contain fail test method cause '
            'its configuration is correct.'
        )

        for i, name in enumerate(expected_test_method_names):
            self.check_generated_test_method(CorrectConfig, name, conf[i],
                                             expected_docs[i], url)
