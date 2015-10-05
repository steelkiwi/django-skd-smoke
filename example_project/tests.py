# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model

from articles.models import Article
from skd_smoke import SmokeTestCase


def create_article(testcase):
    article = Article.objects.create(headline='aaa')
    return {'pk': article.pk}


def get_user(testcase):
    username = 'test_user'
    password = '1234'
    credentials = {'username': username, 'password': password}
    User = get_user_model()
    new_user = User.objects.create(username=username)
    new_user.set_password(password)
    new_user.save()
    testcase.user = new_user
    return credentials


class InitialSmokeTestCase(SmokeTestCase):
    TESTS_CONFIGURATION = (
        # (url, status, method, {
        #       'initialize': None,
        #       'get_url_kwargs': None,
        #       'request_data': None,
        #       'get_user_credentials': None})
        ('admin:login', 200, 'GET'),
        ('articles:articles', 200, 'GET'),
        ('articles:article', 200, 'GET', {'get_url_kwargs': create_article}),
        ('is_authenticated', 302, 'GET'),
        ('is_authenticated', 200, 'GET', {'get_user_credentials': get_user})
    )
