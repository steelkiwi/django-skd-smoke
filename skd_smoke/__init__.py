# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from datetime import datetime
import unittest

from django.core.handlers.wsgi import STATUS_CODE_TEXT
from django.shortcuts import resolve_url


def generate_test_method(urlname, status, method='GET', data=None):
    def new_test_method(self):
        resolved_url = resolve_url(urlname)
        prepared_data = data or {}
        function = getattr(self.client, method.lower())
        response = function(resolved_url, data=prepared_data)
        self.assertEqual(response.status_code, status)
    return new_test_method


def prepare_test_name(urlname, method, status):
    prepared_url = urlname.replace(':', '_').replace('/', '')
    prepared_method = method.lower()
    prepared_time = datetime.now().strftime('%s%f')
    name = 'test_smoke_%(url)s_%(method)s_%(status)s_%(time)s' % {
        'url': prepared_url,
        'method': prepared_method,
        'status': status,
        'time': prepared_time
    }
    return name


class GenerateTestMethodsMeta(type):
    def __new__(mcs, name, bases, attrs):
        for urlname, status, method, data in attrs.get('tests_configuration',
                                                       []):
            status_text = STATUS_CODE_TEXT.get(status, 'UNKNOWN')

            test_method = generate_test_method(urlname, status, method, data)
            test_method.__name__ = name
            test_method.__doc__ = '%s %s %s "%s" %r' % (
                method, urlname, status, status_text, data
            )

            test_method_name = prepare_test_name(urlname, method, status)

            attrs[test_method_name] = test_method
        return super(GenerateTestMethodsMeta, mcs).__new__(
            mcs, name, bases, attrs)


class SmokeGeneratorTestCase(unittest.TestCase):
    __metaclass__ = GenerateTestMethodsMeta

    tests_configuration = ()
