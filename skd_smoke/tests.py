# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from . import SmokeTestCase


class InitialSmokeTestCase(SmokeTestCase):
    """
    Just example of using library. You can test it in your project if you run
    ``./manage.py test skd_smoke``. Correct usage requires subclass creation of
    ``skd_smoke.SmokeTestCase`` inside any of your project ``tests`` module.
    """

    TESTS_CONFIGURATION = (
        # (url, status, method, {
        #       'initialize': None,
        #       'get_url_kwargs': None,
        #       'request_data': None,
        #       'get_user_credentials': None})
        ('admin:login', 200, 'GET'),
        # the same:
        # ('admin:login', 200, 'GET', {}),

        # authenticated users only
        # ('profile', 302, 'GET'),

        # post queries only
        # ('/only_post/, 405, 'GET'),

        # non-existent url
        # ('/something/, 404, 'GET'),

        # initialize
        # ('/list_url/', 200, 'GET', {'initialize': create_list})
    )
