# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse

from articles.models import Article
from skd_smoke import SmokeTestCase


def create_article(testcase):
    article = Article.objects.create(headline='aaa')
    return {'pk': article.pk}


def create_articles(testcase):
    Article.objects.create(headline='aaa')
    Article.objects.create(headline='bbb')


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


def get_article_data(testcase):
    return {'headline': 'new article'}


class InitialSmokeTestCase(SmokeTestCase):
    TESTS_CONFIGURATION = (
        # (url, status, method, {
        #       'comment': None,
        #       'initialize': None,
        #       'url_kwargs': None,
        #       'request_data': None,
        #       'user_credentials': None
        #       'redirect_to': None
        # })
        ('admin:login', 200, 'GET'),

        ('articles:articles', 200, 'GET',
         {'initialize': create_articles}),

        ('articles:article', 200, 'GET',
         {'url_kwargs': create_article}),

        ('articles:create', 302, 'POST',
         {'request_data': get_article_data}),

        ('is_authenticated', 302, 'GET',
         {'comment': 'Anonymous user access with check of redirect url',
          'redirect_to': '%s?next=%s' % (reverse('login'),
                                         reverse('is_authenticated'))}),

        ('is_authenticated', 200, 'GET',
         {'user_credentials': get_user, 'comment': 'Authorized user access'}),
    )
