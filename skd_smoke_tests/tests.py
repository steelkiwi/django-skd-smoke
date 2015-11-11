# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function
import types
from unittest import TestCase

from mock import Mock, patch
from django.core.exceptions import ImproperlyConfigured
from django.core.handlers.wsgi import STATUS_CODE_TEXT
from six import string_types

from skd_smoke import generate_test_method, prepare_test_name, \
    prepare_configuration, generate_fail_test_method, prepare_test_method_doc,\
    SmokeTestCase, EMPTY_TEST_CONFIGURATION_MSG, \
    INCORRECT_TEST_CONFIGURATION_MSG, IMPROPERLY_BUILT_CONFIGURATION_MSG, \
    NOT_REQUIRED_PARAM_TYPE_CHECK, UNSUPPORTED_CONFIGURATION_KEY_MSG, \
    UNKNOWN_HTTP_METHOD_MSG, HTTP_METHODS, LINK_TO_DOCUMENTATION, \
    INCORRECT_REQUIRED_PARAM_TYPE_MSG, REQUIRED_PARAMS, \
    INCORRECT_NOT_REQUIRED_PARAM_TYPE_MSG


class SmokeGeneratorTestCase(TestCase):

    def test_required_params_definition(self):
        for param_setting in REQUIRED_PARAMS:
            self.assertIn('display_name', param_setting)
            self.assertIsInstance(param_setting['display_name'], string_types)
            self.assertIn('expected_type', param_setting)

    def test_non_required_params_definition(self):
        for param_name, param_type in NOT_REQUIRED_PARAM_TYPE_CHECK.items():
            self.assertIsInstance(param_name, string_types)
            self.assertIn('type', param_type)
            self.assertIsInstance(param_type['type'], string_types)
            self.assertIn('func', param_type)
            self.assertTrue(callable(param_type['func']),
                            'Non-required parameter type check func must be '
                            'callable.')

    def test_prepare_configuration(self):
        test = prepare_configuration([('a', 200, 'GET'),
                                      ('b', 200, 'GET')])
        self.assertIsNotNone(test)
        self.assertEqual(
            test, [('a', 200, 'GET', {}), ('b', 200, 'GET', {})])

    def test_prepare_configuration_with_incorrect_http_method(self):
        unknown_http_method = 'unknown'
        with self.assertRaises(ImproperlyConfigured) as cm:
            prepare_configuration([('a', 200, unknown_http_method)])
        raised_exception = cm.exception
        exception_msg = str(raised_exception)
        self.assertIn(UNKNOWN_HTTP_METHOD_MSG % unknown_http_method,
                      exception_msg)

    def test_prepare_configuration_with_all_incorrect_parameters(self):
        incorrect_required_params = [
            100500,  # url should be string_types
            'incorrect',  # status should be int
            666  # method should be string_types
        ]
        incorrect_not_required_params = {
            'redirect_to': 123,  # should be string_types
            'comment': 123,  # should be string_types
            'initialize': 'initialize',  # should be callable
            'url_args': 'url_args',  # should be list or callable
            'url_kwargs': 'url_kwargs',  # should be dict or callable
            'request_data': 'request_data',  # should be dict or callable
            'user_credentials': 'user'  # should be dict or callable
        }
        with self.assertRaises(ImproperlyConfigured) as cm:
            prepare_configuration([
                (incorrect_required_params[0], incorrect_required_params[1],
                 incorrect_required_params[2], incorrect_not_required_params,)
            ])
        raised_exception = cm.exception
        exception_msg = str(raised_exception)
        error_messages = []
        counter = 0
        for param_dict in REQUIRED_PARAMS:
            value = incorrect_required_params[counter]
            error_messages.append(
                INCORRECT_REQUIRED_PARAM_TYPE_MSG % (
                    param_dict['display_name'], counter,
                    param_dict['expected_type'], type(value), value
                )
            )
            counter += 1

        for param, type_info in NOT_REQUIRED_PARAM_TYPE_CHECK.items():
            value = incorrect_not_required_params[param]
            actual_type = type(value)
            error_messages.append(
                INCORRECT_NOT_REQUIRED_PARAM_TYPE_MSG % (
                    param, type_info['type'], actual_type, value
                ))

        error_messages.append(LINK_TO_DOCUMENTATION)
        for error_message in error_messages:
            self.assertIn(error_message, exception_msg)

    def test_prepare_configuration_with_all_http_methods(self):
        config = []
        for http_method in HTTP_METHODS:
            config.append(('url', 200, http_method, {}))
        prepared_config = prepare_configuration(config)
        self.assertEqual(config, prepared_config)

    def test_generate_fail_test_method(self):
        test = generate_fail_test_method('test')
        self.assertIsNotNone(test)
        self.assertEqual(type(test), types.FunctionType)
        self.assertEqual(test.__name__, 'fail_method')

    def test_generate_test_method(self):
        test = generate_test_method('urlname', 200)
        self.assertIsNotNone(test)
        self.assertEqual(type(test), types.FunctionType)
        self.assertEqual(test.__name__, 'new_test_method')

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
        self.assertEqual(test, 'GET urlname 200 "status_text" {}')


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
        docs = []
        for c in configuration:
            if c[-1]:
                conf_value = c[-1].get('request_data', {})
                if callable(conf_value):
                    request_data = conf_value.__name__
                else:
                    request_data = conf_value
                comment = c[-1].get('comment', None)
            else:
                comment = None
                request_data = {}
            doc = '%(method)s %(url)s %(status_code)s "%(status)s" ' \
                  '%(request_data)r' % {
                            'method': c[2],
                            'url': c[0],
                            'status_code': c[1],
                            'status': STATUS_CODE_TEXT.get(c[1], 'UNKNOWN'),
                            'request_data': request_data
                        }
            if comment:
                doc = '%s %s' % (doc, comment)
            docs.append(doc)

        return docs

    def assert_called_fail_test_method(self, cls, msg):
        mock = self.call_cls_method_by_name(cls, 'FAIL_METHOD_NAME')
        self.assertEqual(mock.fail.call_count, 1)
        self.assertIn(msg, mock.fail.call_args_list[0][0][0])

    def assert_generated_test_method(self, cls, name, configuration, doc, url,
                                     user_credentials=None, redirect_to=None):
        # check existence
        self.assertTrue(hasattr(cls, name),
                        'There is no "%s" in %s but should be.' % (name, cls))

        test_method = getattr(cls, name)
        _, status_code, method, params = configuration
        method_lower = method.lower()

        # check __name__
        self.assertEqual(test_method.__name__, name)

        # check __doc__
        self.assertEqual(test_method.__doc__, doc)

        method_mock = Mock()
        method_mock.return_value = response = Mock(status_code=status_code)

        method_mocks = {method_lower: method_mock}

        if user_credentials:
            login_mock = Mock()
            method_mocks['login'] = login_mock

        # check actual run
        client_mock = Mock(**method_mocks)

        testcase_mock = Mock(spec=cls, assertEqual=Mock(), client=client_mock,
                             assertTrue=Mock(), assertRedirects=Mock())
        test_method(testcase_mock)

        request_data = params.get('request_data', {})
        if callable(request_data):
            request_data = request_data(testcase_mock)
        getattr(client_mock, method_lower).assert_called_once_with(
            url, data=request_data)
        testcase_mock.assertEqual.assert_called_once_with(
            status_code, status_code)

        if user_credentials:
            login_mock.assert_called_once_with(**user_credentials)

        if redirect_to:
            testcase_mock.assertRedirects.assert_called_once_with(
                response, redirect_to, fetch_redirect_response=False
            )
        else:
            testcase_mock.assertRedirects.assert_not_called()

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
            'url_kwargs': lambda _: None,

            # start unsupported data keys
            'unsupported_param1': 1,
            'unsupported_param2': 2,
            # end unsupported data keys
        }
        conf = (
            ('url', 200, 'GET', data),
        )

        unsupported_keys = set(data.keys()) - \
                           set(NOT_REQUIRED_PARAM_TYPE_CHECK.keys())

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
            ('/some_url/', 302, 'GET', {'comment': 'text comment'}),
            ('/comments/', 201, 'POST',
             {'request_data': {'message': 'new comment'}}),
            ('namespace:url', 200, 'GET', {}),
            ('some_url2', 200, 'GET', {}),
        )

        expected_test_method_names = [
            'test_smoke_some_url_get_302_ffffffff',
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
    def test_generated_test_method_with_redirect_to_setting(
            self, mock_django_resolve_url, mock_uuid4):

        redirect_url = '/redirect_url/'

        conf = (
            ('urlname', 302, 'GET', {'redirect_to': redirect_url}),
        )

        expected_test_method_names = [
            'test_smoke_urlname_get_302_ffffffff',
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
            expected_docs[0], url, redirect_to=redirect_url)

    @patch('skd_smoke.uuid4')
    @patch('skd_smoke.resolve_url')
    def test_generated_test_method_with_initialize_callable(
            self, mock_django_resolve_url, mock_uuid4):

        initialize_mock = Mock()

        conf = (
            ('urlname_with_slug', 200, 'GET', {'initialize': initialize_mock}),
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

        self.assertEqual(initialize_mock.call_count, 1)

    @patch('skd_smoke.uuid4')
    @patch('skd_smoke.resolve_url')
    def test_generated_test_method_with_url_kwargs_as_dict(
            self, mock_django_resolve_url, mock_uuid4):

        url_kwargs = {'slug': 'cool_article'}

        conf = (
            ('urlname_with_slug', 200, 'GET',
             {'url_kwargs': url_kwargs}),
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

    @patch('skd_smoke.uuid4')
    @patch('skd_smoke.resolve_url')
    def test_generated_test_method_with_url_kwargs_as_callable(
            self, mock_django_resolve_url, mock_uuid4):

        url_kwargs = {'slug': 'cool_article'}

        def get_url_kwargs(testcase):
            return url_kwargs

        conf = (
            ('urlname_with_slug', 200, 'GET',
             {'url_kwargs': get_url_kwargs}),
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

    @patch('skd_smoke.uuid4')
    @patch('skd_smoke.resolve_url')
    def test_generated_test_method_with_url_args_as_dict(
            self, mock_django_resolve_url, mock_uuid4):

        url_args = ['arg1']

        conf = (
            ('urlname_with_arg', 200, 'GET',
             {'url_args': url_args}),
        )

        expected_test_method_names = [
            'test_smoke_urlname_with_arg_get_200_ffffffff',
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
            conf[0][0], *url_args)

    @patch('skd_smoke.uuid4')
    @patch('skd_smoke.resolve_url')
    def test_generated_test_method_with_url_args_as_callable(
            self, mock_django_resolve_url, mock_uuid4):

        url_args = ['arg1']

        def get_url_args(testcase):
            return url_args

        conf = (
            ('urlname_with_arg', 200, 'GET',
             {'url_args': get_url_args}),
        )

        expected_test_method_names = [
            'test_smoke_urlname_with_arg_get_200_ffffffff',
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
        # url kwargs returned from call of get_url_args() method
        mock_django_resolve_url.assert_called_once_with(
            conf[0][0], *url_args)

    @patch('skd_smoke.uuid4')
    @patch('skd_smoke.resolve_url')
    def test_generated_test_method_with_user_credentials_as_dict(
            self, mock_django_resolve_url, mock_uuid4):

        user_credentials = {'username': 'test_user', 'password': '1234'}

        conf = (
            ('urlname_with_slug', 200, 'GET',
             {'user_credentials': user_credentials}),
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
            expected_docs[0], url, user_credentials)

    @patch('skd_smoke.uuid4')
    @patch('skd_smoke.resolve_url')
    def test_generated_test_method_with_user_credentials_as_callable(
            self, mock_django_resolve_url, mock_uuid4):

        user_credentials = {'username': 'test_user', 'password': '1234'}

        def get_user_creadentials(testcase):
            return user_credentials

        conf = (
            ('urlname_with_slug', 200, 'GET',
             {'user_credentials': get_user_creadentials}),
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
            expected_docs[0], url, user_credentials)

    @patch('skd_smoke.uuid4')
    @patch('skd_smoke.resolve_url')
    def test_generated_test_method_with_request_data_as_dict(
            self, mock_django_resolve_url, mock_uuid4):

        request_data = {'message': 'new comment'}

        conf = (
            ('/some_url/', 200, 'GET', {}),
            ('/comments/', 201, 'POST',
             {'request_data': request_data}),
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
    def test_generated_test_method_with_request_data_as_callable(
            self, mock_django_resolve_url, mock_uuid4):

        request_data = {'message': 'new comment'}

        def get_request_data(testcase):
            return request_data

        conf = (
            ('/some_url/', 200, 'GET', {}),
            ('/comments/', 201, 'POST',
             {'request_data': get_request_data}),
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
