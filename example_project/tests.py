# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from skd_smoke import SmokeTestCase


class ExampleProjectSmokeTestCase(SmokeTestCase):
    TESTS_CONFIGURATION = (
        # (url, status, method, data=None)
        ('admin:login', 200, 'GET'),
        ('login', 200, 'GET'),
        ('is_authenticated', 302, 'GET'),
        ('only_post_request', 405, 'GET'),
        ('only_post_request', 200, 'POST'),
        ('non_existent_url', 404, 'GET'),
        ('non_existent_url', 404, 'POST'),
        ('/non_existent_url2/', 404, 'GET'),
        ('/non_existent_url2/', 404, 'POST'),
    )
