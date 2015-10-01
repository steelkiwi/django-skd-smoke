# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import types
from unittest import TestCase
from mock import Mock, patch
from django.core.handlers.wsgi import STATUS_CODE_TEXT
from skd_smoke import generate_test_method, prepare_test_name, \
    prepare_configuration, generate_fail_test_method, prepare_test_method_doc,\
    SmokeTestCase, EMPTY_TEST_CONFIGURATION_MSG, \
    INCORRECT_TEST_CONFIGURATION_MSG, IMPROPERLY_BUILT_CONFIGURATION_MSG, \
    CONFIGURATION_KEYS, UNSUPPORTED_CONFIGURATION_KEY_MSG


class SmokeGeneratorTestCase(TestCase):

    def test_prepare_configuration(self):
        test = prepare_configuration([('a', 200, 'GET'),
                                      ('b', 200, 'GET')])
        self.assertIsNotNone(test)
        self.assertEquals(
            test, [('a', 200, 'GET', {}), ('b', 200, 'GET', {})])

    def test_generate_fail_test_method(self):
        test = generate_fail_test_method('test')
        self.assertIsNotNone(test)
        self.assertEquals(type(test), types.FunctionType)
        self.assertEquals(test.__name__, 'fail_method')

    def test_generate_test_method(self):
        test = generate_test_method('urlname', 200)
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
        self.assertEquals(test, 'GET urlname 200 "status_text" {}')


class SmokeTestCaseTestCase(TestCase):

    def check_if_class_contains_test_methods(self, cls, prefix='test_smoke'):

        for attr in cls.__dict__:
            if attr.startswith(prefix):
                return True

        return False

    def check_if_class_contains_fail_test_method(self, cls):
        return hasattr(cls, getattr(cls, 'FAIL_METHOD_NAME'))

    def call_cls_method_by_name(self, cls, name):
        method_name = getattr(cls, name)
        test_method = getattr(cls, method_name)

        mock = Mock(spec=cls)
        test_method(mock)
        return mock

    def generate_docs_from_configuration(self, configuration):
        return [
            '%(method)s %(url)s %(status_code)s "%(status)s" %(request_data)r'
            % {
                'method': c[2],
                'url': c[0],
                'status_code': c[1],
                'status': STATUS_CODE_TEXT.get(c[1], 'UNKNOWN'),
                'request_data': c[3].get('request_data', {}) if c[3] else {}
            } for c in configuration
        ]

    def assert_called_fail_test_method(self, cls, msg):
        mock = self.call_cls_method_by_name(cls, 'FAIL_METHOD_NAME')
        self.assertEqual(mock.fail.call_count, 1)
        self.assertIn(msg, mock.fail.call_args_list[0][0][0])

    def assert_generated_test_method(self, cls, name, configuration, doc, url):
        # check existence
        self.assertTrue(hasattr(cls, name),
                        'There is no "%s" in %s but should be.' % (name, cls))

        test_method = getattr(cls, name)
        _, status_code, method, params = configuration
        request_data = params.get('request_data', {})
        method_lower = method.lower()

        # check __name__
        self.assertEqual(test_method.__name__, name)

        # check __doc__
        self.assertEqual(test_method.__doc__, doc)

        method_mock = Mock()
        method_mock.return_value = Mock(status_code=status_code)

        # check actual run
        client_mock = Mock(**{method_lower: method_mock})

        testcase_mock = Mock(spec=cls, assertEqual=Mock(), client=client_mock)
        test_method(testcase_mock)
        getattr(client_mock, method_lower).assert_called_once_with(
            url, data=request_data)
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

        self.assert_called_fail_test_method(
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

        self.assert_called_fail_test_method(
            BrokenConfig, INCORRECT_TEST_CONFIGURATION_MSG)

    def test_configuration_built_incorrectly1(self):
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

        self.assert_called_fail_test_method(
            BrokenConfig, IMPROPERLY_BUILT_CONFIGURATION_MSG)

    def test_configuration_built_incorrectly2(self):
        data = {
            'request_data': {'param': 'value'},
            'get_url_kwargs': lambda: None,

            # start unsupported data keys
            'unsupported_param1': 1,
            'unsupported_param2': 2,
            # end unsupported data keys
        }
        conf = (
            ('url', 200, 'GET', data),
        )

        unsupported_keys = set(data.keys()) - CONFIGURATION_KEYS

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

        self.assert_called_fail_test_method(
            BrokenConfig,
            UNSUPPORTED_CONFIGURATION_KEY_MSG % ', '.join(unsupported_keys)
        )

    def test_simple_correct_configuration(self):
        conf = (
            ('a', 200, 'GET', {}),
        )

        CorrectConfig = type(
            str('CorrectConfig'),
            (SmokeTestCase,),
            {'TESTS_CONFIGURATION': conf})

        if self.check_if_class_contains_fail_test_method(CorrectConfig):
            mock = self.call_cls_method_by_name(CorrectConfig,
                                                'FAIL_METHOD_NAME')
            self.fail(
                'Generated TestCase contains fail test method but should not '
                'cause its configuration is correct. Error stacktrace:\n%s' %
                mock.fail.call_args_list[0][0][0]
            )

        self.assertTrue(
            self.check_if_class_contains_test_methods(CorrectConfig),
            'TestCase should contain at least one generated test method.'
        )

    @patch('skd_smoke.uuid4')
    @patch('skd_smoke.resolve_url')
    def test_simple_generated_test_methods(self, mock_django_resolve_url,
                                           mock_uuid4):
        conf = (
            ('/some_url/', 200, 'GET', {}),
            ('/comments/', 201, 'POST',
             {'request_data': {'message': 'new comment'}}),
            ('namespace:url', 200, 'GET', {}),
            ('some_url2', 200, 'GET', {}),
        )

        expected_test_method_names = [
            'test_smoke_some_url_get_200_ffffffff',
            'test_smoke_comments_post_201_ffffffff',
            'test_smoke_namespace_url_get_200_ffffffff',
            'test_smoke_some_url2_get_200_ffffffff',
        ]

        expected_docs = self.generate_docs_from_configuration(conf)

        mock_django_resolve_url.return_value = url = '/url/'
        mock_uuid4.return_value = Mock(hex='ffffffff')

        CorrectConfig = type(
            str('CorrectConfig'),
            (SmokeTestCase,),
            {'TESTS_CONFIGURATION': conf})

        if self.check_if_class_contains_fail_test_method(CorrectConfig):
            mock = self.call_cls_method_by_name(CorrectConfig,
                                                'FAIL_METHOD_NAME')
            self.fail(
                'Generated TestCase contains fail test method but should not '
                'cause its configuration is correct. Error stacktrace:\n%s' %
                mock.fail.call_args_list[0][0][0]
            )

        self.assertTrue(
            self.check_if_class_contains_test_methods(CorrectConfig),
            'TestCase should contain at least one generated test method.'
        )

        for i, name in enumerate(expected_test_method_names):
            self.assert_generated_test_method(CorrectConfig, name, conf[i],
                                              expected_docs[i], url)

    @patch('skd_smoke.uuid4')
    @patch('skd_smoke.resolve_url')
    def test_generated_test_method_with_method_in_config(
            self, mock_django_resolve_url, mock_uuid4):

        url_kwargs = {'slug': 'cool_article'}

        def get_url_kwargs():
            return url_kwargs

        conf = (
            ('urlname_with_slug', 200, 'GET',
             {'get_url_kwargs': get_url_kwargs}),
        )

        expected_test_method_names = [
            'test_smoke_urlname_with_slug_get_200_ffffffff',
        ]

        expected_docs = self.generate_docs_from_configuration(conf)

        mock_django_resolve_url.return_value = url = '/url/'
        mock_uuid4.return_value = Mock(hex='ffffffff')

        CorrectConfig = type(
            str('CorrectConfig'),
            (SmokeTestCase,),
            {'TESTS_CONFIGURATION': conf})

        if self.check_if_class_contains_fail_test_method(CorrectConfig):
            mock = self.call_cls_method_by_name(CorrectConfig,
                                                'FAIL_METHOD_NAME')
            self.fail(
                'Generated TestCase contains fail test method but should not '
                'cause its configuration is correct. Error stacktrace:\n%s' %
                mock.fail.call_args_list[0][0][0]
            )

        self.assertTrue(
            self.check_if_class_contains_test_methods(CorrectConfig),
            'TestCase should contain at least one generated test method.'
        )

        self.assert_generated_test_method(
            CorrectConfig, expected_test_method_names[0], conf[0],
            expected_docs[0], url)

        # actual check that resolve_url was called with correct urlname AND
        # url kwargs returned from call of get_url_kwargs() method
        mock_django_resolve_url.assert_called_once_with(
            conf[0][0], **url_kwargs)
