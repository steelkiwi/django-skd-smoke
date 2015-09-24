# -*- coding: utf-8 -*-
from __future__ import unicode_literals
from importlib import import_module

from django.core.exceptions import ImproperlyConfigured
from django.test import TestCase

from . import SmokeGeneratorTestCase
from . import app_settings


TESTS_CONFIGURATION = []

try:
    tests_config_module = import_module(
        app_settings.SKD_SMOKE_TESTS_CONFIG_MODULE)
except Exception as e:
    print 'Error during import of django-skd-smoke config module'
    raise
else:
    if hasattr(tests_config_module, 'TESTS_CONFIGURATION') and \
            isinstance(tests_config_module.TESTS_CONFIGURATION, (tuple, list)):

        for test_config in tests_config_module.TESTS_CONFIGURATION:
            if len(test_config) == 3:
                test_config += (None,)
            elif len(test_config) == 4:
                pass
            else:
                raise ImproperlyConfigured(
                    'Every test method config should contain three or four '
                    'elements (url, status, method, data=None). Please review '
                    'skd_smoke/smoketests_example.py or refer to documention '
                    'on https://github.com/steelkiwi/django-skd-smoke')

            TESTS_CONFIGURATION.append(test_config)
    else:
        raise ImproperlyConfigured(
            'django-skd-smoke config module should define '
            'TESTS_CONFIGURATION list or tuple. Please review '
            'skd_smoke/smoketests_example.py or refer to project '
            'documention on https://github.com/steelkiwi/django-skd-smoke')


class SmokeTestCase(SmokeGeneratorTestCase, TestCase):
    tests_configuration = TESTS_CONFIGURATION
