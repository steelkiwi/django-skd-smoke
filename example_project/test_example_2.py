# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# add to readme starting from:
from skd_smoke import SmokeTestCase

from articles.models import Article


def create_articles(testcase):
    for i in range(3):
        Article.objects.create(headline='article #%s' % i)


class ArticlesListSmokeTestCase(SmokeTestCase):
    TESTS_CONFIGURATION = (
        ('articles:articles', 200, 'GET',
            {'initialize': create_articles}  # pass your func here
        ),
    )
