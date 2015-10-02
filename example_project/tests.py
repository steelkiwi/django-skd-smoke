# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from articles.models import Article
from skd_smoke import SmokeTestCase


def create_article():
    article = Article.objects.create(headline='aaa')
    return {'pk': article.pk}


class InitialSmokeTestCase(SmokeTestCase):
    TESTS_CONFIGURATION = (
        # (url, status, method, {'get_url_kwargs': None, 'request_data': None})
        ('admin:login', 200, 'GET'),
        ('articles:articles', 200, 'GET'),
        ('articles:article', 200, 'GET', {'get_url_kwargs': create_article}),
    )
