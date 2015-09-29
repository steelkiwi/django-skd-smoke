# -*- coding: utf-8 -*-
from __future__ import unicode_literals, print_function

import traceback
from uuid import uuid4

from django.core.exceptions import ImproperlyConfigured
from django.core.handlers.wsgi import STATUS_CODE_TEXT
from django.shortcuts import resolve_url

from django.test import TestCase
from django.utils import six

IMPROPERLY_BUILT_CONFIGURATION_MSG = \
    'Every test method config should contain three or four elements (url, ' \
    'status, method, data=None). Please review skd_smoke/tests.py or refer ' \
    'to documentation on https://github.com/steelkiwi/django-skd-smoke'

EMPTY_TEST_CONFIGURATION_MSG = \
    'django-skd-smoke TestCase has empty TESTS_CONFIGURATION. Please review ' \
    'skd_smoke/tests.py or refer to project documentation on ' \
    'https://github.com/steelkiwi/django-skd-smoke'

INCORRECT_TEST_CONFIGURATION_MSG = \
    'django-skd-smoke TestCase should define TESTS_CONFIGURATION list or ' \
    'tuple. Please review skd_smoke/tests.py or refer to project ' \
    'documentation on https://github.com/steelkiwi/django-skd-smoke'

UNSUPPORTED_CONFIGURATION_KEY_MSG = \
    'django-skd-smoke configuration does not support this key: "%s".'

CONFIGURATION_KEYS = {'get_url_kwargs', 'request_data'}


def prepare_configuration(tests_configuration):
    confs = []

    if isinstance(tests_configuration, (tuple, list)):

        for test_config in tests_configuration:
            if len(test_config) == 3:
                test_config += ({},)
            elif len(test_config) == 4:
                diff = set(test_config[3].keys()) - CONFIGURATION_KEYS
                if diff:
                    raise ImproperlyConfigured(
                        UNSUPPORTED_CONFIGURATION_KEY_MSG % ', '.join(diff))

            else:
                raise ImproperlyConfigured(IMPROPERLY_BUILT_CONFIGURATION_MSG)

            confs.append(test_config)

        if not confs:
            raise ImproperlyConfigured(EMPTY_TEST_CONFIGURATION_MSG)

    else:
        raise ImproperlyConfigured(INCORRECT_TEST_CONFIGURATION_MSG)

    return confs


def generate_fail_test_method(exception_stacktrace):
    def fail_method(self):
        self.fail(exception_stacktrace)
    return fail_method


def generate_test_method(urlname, status, method='GET', get_url_kwargs=None,
                         request_data=None):
    def new_test_method(self):
        if get_url_kwargs:
            resolved_url = resolve_url(urlname, **get_url_kwargs())
        else:
            resolved_url = resolve_url(urlname)
        prepared_data = request_data or {}
        function = getattr(self.client, method.lower())
        response = function(resolved_url, data=prepared_data)
        self.assertEqual(response.status_code, status)
    return new_test_method


def prepare_test_name(urlname, method, status):
    prepared_url = urlname.replace(':', '_').strip('/').replace('/', '_')
    prepared_method = method.lower()
    name = 'test_smoke_%(url)s_%(method)s_%(status)s_%(uuid)s' % {
        'url': prepared_url,
        'method': prepared_method,
        'status': status,
        'uuid': uuid4().hex
    }
    return name


def prepare_test_method_doc(method, urlname, status, status_text, data):
    data = data or {}
    return '%(method)s %(urlname)s %(status)s "%(status_text)s" %(data)r' % {
        'method': method,
        'urlname': urlname,
        'status': status,
        'status_text': status_text,
        'data': data
    }


class GenerateTestMethodsMeta(type):
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
                get_url_kwargs = data.get('get_url_kwargs', None)
                request_data = data.get('request_data', None)
                status_text = STATUS_CODE_TEXT.get(status, 'UNKNOWN')

                test_method_name = prepare_test_name(urlname, method, status)

                test_method = generate_test_method(
                    urlname, status, method, get_url_kwargs, request_data)
                test_method.__name__ = str(test_method_name)
                test_method.__doc__ = prepare_test_method_doc(
                    method, urlname, status, status_text, request_data)

                setattr(cls, test_method_name, test_method)

        return cls


class SmokeTestCase(six.with_metaclass(GenerateTestMethodsMeta, TestCase)):
    TESTS_CONFIGURATION = None
    FAIL_METHOD_NAME = 'test_fail_cause_bad_configuration'
