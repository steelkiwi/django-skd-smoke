# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import traceback
from uuid import uuid4
from six import string_types

from django.core.exceptions import ImproperlyConfigured
from django.core.handlers.wsgi import STATUS_CODE_TEXT
from django.shortcuts import resolve_url

from django.test import TestCase
from django.utils import six

# start configuration error messages
IMPROPERLY_BUILT_CONFIGURATION_MSG = \
    'Every test method config should contain three or four elements (url, ' \
    'status, method, data=None).'

EMPTY_TEST_CONFIGURATION_MSG = \
    'django-skd-smoke TestCase has empty TESTS_CONFIGURATION.'

INCORRECT_TEST_CONFIGURATION_MSG = \
    'django-skd-smoke TestCase should define TESTS_CONFIGURATION list or ' \
    'tuple.'

UNSUPPORTED_CONFIGURATION_KEY_MSG = \
    'django-skd-smoke configuration does not support those keys: %s.'


REQUIRED_PARAMS = (
    {'display_name': 'url', 'expected_type': string_types},
    {'display_name': 'status', 'expected_type': int},
    {'display_name': 'method', 'expected_type': string_types},
)


def check_type(types):
    def check(obj):
        return isinstance(obj, types)
    return check


def dict_or_callable(d):
    return isinstance(d, dict) or callable(d)

# name and function
NOT_REQUIRED_PARAM_TYPE_CHECK = {
    'comment': {'type': 'string', 'func': check_type(string_types)},
    'initialize': {'type': 'callable', 'func': callable},
    'url_kwargs': {'type': 'dict or callable', 'func': dict_or_callable},
    'request_data': {'type': 'dict or callable', 'func': dict_or_callable},
    'user_credentials': {'type': 'dict or callable', 'func': dict_or_callable},
    'redirect_to': {'type': 'string', 'func': check_type(string_types)},
}

INCORRECT_REQUIRED_PARAM_TYPE_MSG = \
    'django-skd-smoke: Configuration parameter "%s" with index=%s should be ' \
    '%s but is %s with next value: %s.'

INCORRECT_NOT_REQUIRED_PARAM_TYPE_MSG = \
    'django-skd-smoke: Configuration parameter "%s" should be ' \
    '%s but is %s with next value: %s.'

LINK_TO_DOCUMENTATION = 'For more information please review ' \
    'skd_smoke/tests.py or refer to project documentation on ' \
    'https://github.com/steelkiwi/django-skd-smoke#configuration.'

UNKNOWN_HTTP_METHOD_MSG = \
    'Your django-skd-smoke configuration defines unknown http method: "%s".'

HTTP_METHODS = {'get', 'post', 'head', 'options', 'put', 'patch', 'detete',
                'trace'}

INCORRECT_USER_CREDENTIALS = \
    'Authentication process failed. Supplied user credentials are incorrect: '\
    '%r. Ensure that related user was created successfully.'

# end configuration error messages


def append_doc_link(error_message):
    return error_message + '\n' + LINK_TO_DOCUMENTATION


def prepare_configuration(tests_configuration):
    """
    Prepares initial tests configuration. Raises exception if there is any
    problem with it.

    :param tests_configuration: initial tests configuration as tuple or list \
        with predefined structure
    :return: adjusted configuration which should be used further
    :raises: ``django.core.exceptions.ImproperlyConfigured`` if there is any \
        problem with supplied ``tests_configuration``
    """
    confs = []

    if isinstance(tests_configuration, (tuple, list)):

        number_of_required_params = len(REQUIRED_PARAMS)
        total_number_of_params = number_of_required_params + 1

        for test_config in tests_configuration:
            if len(test_config) == number_of_required_params:
                test_config += ({},)
                check_dict = False
            elif len(test_config) == total_number_of_params:
                diff = set(test_config[-1].keys()) - \
                       set(NOT_REQUIRED_PARAM_TYPE_CHECK.keys())
                if diff:
                    raise ImproperlyConfigured(
                        append_doc_link(UNSUPPORTED_CONFIGURATION_KEY_MSG %
                                        ', '.join(diff))
                    )
                check_dict = True
            else:
                raise ImproperlyConfigured(
                    append_doc_link(IMPROPERLY_BUILT_CONFIGURATION_MSG)
                )

            type_errors = []

            # required params check
            for idx, required_param in enumerate(test_config[:3]):
                required_type = REQUIRED_PARAMS[idx]['expected_type']
                if not isinstance(required_param, required_type):
                    type_errors.append(
                        INCORRECT_REQUIRED_PARAM_TYPE_MSG %
                        (REQUIRED_PARAMS[idx]['display_name'], idx,
                         required_type, type(required_param), required_param)
                    )

            http_method = test_config[2]
            if isinstance(http_method, REQUIRED_PARAMS[2]['expected_type']) \
                    and http_method.lower() not in HTTP_METHODS:
                type_errors.append(UNKNOWN_HTTP_METHOD_MSG % http_method)

            # not required params check
            if check_dict:
                for key, value in test_config[-1].items():
                    type_info = NOT_REQUIRED_PARAM_TYPE_CHECK[key]
                    function = type_info['func']
                    if not function(value):
                        type_errors.append(
                            INCORRECT_NOT_REQUIRED_PARAM_TYPE_MSG %
                            (key, type_info['type'], type(value), value)
                        )

            if type_errors:
                type_errors.append(LINK_TO_DOCUMENTATION)
                raise ImproperlyConfigured('\n'.join(type_errors))

            confs.append(test_config)

        if not confs:
            raise ImproperlyConfigured(
                append_doc_link(EMPTY_TEST_CONFIGURATION_MSG))

    else:
        raise ImproperlyConfigured(
            append_doc_link(INCORRECT_TEST_CONFIGURATION_MSG))

    return confs


def generate_fail_test_method(exception_stacktrace):
    """
    Generates test method which fails and informs user about occurred
    exception.

    :param exception_stacktrace: stacktrace of occurred exception
    :return: method which takes ``TestCase`` and calls its ``fail`` method \
        with provided ``exception_stacktrace``
    """
    def fail_method(self):
        self.fail(exception_stacktrace)
    return fail_method


def generate_test_method(urlname, status, method='GET', initialize=None,
                         url_kwargs=None, request_data=None,
                         user_credentials=None, redirect_to=None):
    """
    Generates test method which calls ``get_url_kwargs`` callable if any,
    resolves supplied ``urlname``, calls proper ``self.client`` method (get,
    post, etc.) with ``request_data`` if any and compares response status with
    parameter ``status`` using ``assertEqual``.

    :param urlname: plain url or urlname or namespace:urlname
    :param status: http status code
    :param method: http method (get, post, etc.)
    :param initialize: callable object which is called in the very beginning \
        of test method
    :param url_kwargs: dict or callable object which returns kwargs dict to \
        resolve url using ``django.shortcuts.resolve_url``
    :param request_data: dict or callable object which returns dict to pass it\
        into http method request
    :param user_credentials: dict or callable object which returns dict to \
        login user using ``TestCase.client.login``
    :param redirect_to: plain url which is checked if only expected status \
        code is one of the [301, 302, 303, 307]
    :return: new test method

    """
    def new_test_method(self):
        if initialize:
            initialize(self)
        if callable(url_kwargs):
            prepared_url_kwargs = url_kwargs(self)
        else:
            prepared_url_kwargs = url_kwargs or {}

        resolved_url = resolve_url(urlname, **prepared_url_kwargs)

        if user_credentials:
            if callable(user_credentials):
                credentials = user_credentials(self)
            else:
                credentials = user_credentials
            logged_in = self.client.login(**credentials)
            self.assertTrue(
                logged_in, INCORRECT_USER_CREDENTIALS % credentials)
        function = getattr(self.client, method.lower())
        if callable(request_data):
            prepared_data = request_data(self)
        else:
            prepared_data = request_data or {}
        response = function(resolved_url, data=prepared_data)
        self.assertEqual(response.status_code, status)
        if status in (301, 302, 303, 307) and redirect_to:
            self.assertRedirects(response, redirect_to)
    return new_test_method


def prepare_test_name(urlname, method, status):
    """
    Prepares name for smoke test method with supplied parameters.

    :param urlname: initial urlname
    :param method: http method (get, post, etc.)
    :param status: http status code
    :return: test name
    """
    prepared_url = urlname.replace(':', '_').strip('/').replace('/', '_')
    prepared_method = method.lower()
    name = 'test_smoke_%(url)s_%(method)s_%(status)s_%(uuid)s' % {
        'url': prepared_url,
        'method': prepared_method,
        'status': status,
        'uuid': uuid4().hex
    }
    return name


def prepare_test_method_doc(method, urlname, status, status_text, data,
                            comment=None):
    """
    Prepares doc string to describe called http query.

    :param method: http method (get, post, etc.)
    :param urlname: initial urlname
    :param status: http status code
    :param status_text: humanized http status
    :param data: request data as dict or callable
    :param comment: comment is added to the end of the result
    :return: doc string
    """
    if callable(data):
        data = data.__name__
    else:
        data = data or {}
    result = '%(method)s %(urlname)s %(status)s "%(status_text)s" %(data)r' % {
        'method': method.upper(),
        'urlname': urlname,
        'status': status,
        'status_text': status_text,
        'data': data
    }
    # append comment to the end if any
    if comment:
        result = '%s %s' % (result, comment)
    return result


class GenerateTestMethodsMeta(type):
    """
    Metaclass which creates new test methods according to tests configuration.
    It adds them to subclass instances only. So the first user class of this
    metaclass will not got anything. It's done in order to have
    ``SmokeTestCase`` defined inside our project and give possibility to
    derive it anywhere without duplicating test methods creation
    (in ``SmokeTestCase`` and library user test case).
    """

    def __new__(mcs, name, bases, attrs):
        cls = super(GenerateTestMethodsMeta, mcs).__new__(
            mcs, name, bases, attrs)

        # Ensure test method generation is only performed for subclasses of
        # GenerateTestMethodsMeta (excluding GenerateTestMethodsMeta class
        # itself).
        parents = [b for b in bases if isinstance(b, GenerateTestMethodsMeta)]
        if not parents:
            return cls

        # noinspection PyBroadException
        try:
            config = prepare_configuration(cls.TESTS_CONFIGURATION)
        except Exception:
            fail_method = generate_fail_test_method(traceback.format_exc())
            fail_method_name = cls.FAIL_METHOD_NAME
            fail_method.__name__ = str(fail_method_name)

            setattr(cls, fail_method_name, fail_method)
        else:
            for urlname, status, method, data in config:
                comment = data.get('comment', None)
                initialize = data.get('initialize', None)
                get_url_kwargs = data.get('url_kwargs', None)
                request_data = data.get('request_data', None)
                get_user_credentials = data.get('user_credentials', None)
                redirect_to = data.get('redirect_to', None)
                status_text = STATUS_CODE_TEXT.get(status, 'UNKNOWN')

                test_method_name = prepare_test_name(urlname, method, status)

                test_method = generate_test_method(
                    urlname, status, method, initialize, get_url_kwargs,
                    request_data, get_user_credentials, redirect_to
                )
                test_method.__name__ = str(test_method_name)
                test_method.__doc__ = prepare_test_method_doc(
                    method, urlname, status, status_text, request_data,
                    comment
                )

                setattr(cls, test_method_name, test_method)

        return cls


class SmokeTestCase(six.with_metaclass(GenerateTestMethodsMeta, TestCase)):
    """
    TestCase which should be derived by any library user. It's required
    to define ``TESTS_CONFIGURATION`` inside subclass. It should be defined as
    tuple or list of tuples with next structure:

        (url, status, method,
            {'comment': None, 'initialize': None,
            'url_kwargs': None, 'request_data': None,
            'user_credentials': None, 'redirect_to': None})

    For more information please refer to project documentation:
    https://github.com/steelkiwi/django-skd-smoke#configuration
    """

    TESTS_CONFIGURATION = None
    FAIL_METHOD_NAME = 'test_fail_cause_bad_configuration'
