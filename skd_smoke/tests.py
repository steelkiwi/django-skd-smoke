# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from . import SmokeTestCase


class InitialSmokeTestCase(SmokeTestCase):
    TESTS_CONFIGURATION = (
        # (url, status, method, data=None)
        ('admin:login', 200, 'GET'),
        # the same:
        # ('admin:login', 200, 'GET', None),

        # authenticated users only
        # ('profile', 302, 'GET'),

        # post queries only
        # ('/only_post/, 405, 'GET'),

        # non-existent url
        # ('/something/, 404, 'GET'),
    )
