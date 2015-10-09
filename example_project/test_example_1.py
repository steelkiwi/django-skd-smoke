# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# add to readme starting from:
from django.contrib.auth import get_user_model

from skd_smoke import SmokeTestCase


def get_article_data(testcase):
    return {'headline': 'new article'}


def get_user_credentials(testcase):
    username = 'test_user'
    password = '1234'
    credentials = {'username': username, 'password': password}
    User = get_user_model()
    new_user = User.objects.create(username=username)
    new_user.set_password(password)
    new_user.save()
    testcase.user = new_user
    return credentials


class SimpleSmokeTestCase(SmokeTestCase):
    TESTS_CONFIGURATION = (
        ('home', 200, 'GET',),  # 1
        ('home', 200, 'GET', {'request_data': {'scrollTop': 1}}),  # 2
        ('articles:create', 200, 'POST',),  # 3
        ('articles:create', 302, 'POST',
         {'request_data': get_article_data}),  # 4
        ('is_authenticated', 302, 'GET',),  # 5
        ('is_authenticated', 200, 'GET',
         {'user_credentials': get_user_credentials}),  # 6
        ('/only_post_request/', 405, 'GET',),  # 7
    )
