# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# add to readme starting from:
from django.contrib.auth import get_user_model

from skd_smoke import SmokeTestCase

from articles.models import Article


def create_user():
    UserModel = get_user_model()
    new_user = UserModel.objects.create(username='test_user')
    new_user.set_password('1234')
    new_user.save()
    return new_user


def create_unpublished_article(commit=True):
    article = Article(headline='unpublished', published=False)
    if commit:
        article.save()
    return article


def create_article_without_owner(testcase):
    return {'pk': create_unpublished_article().pk}


def create_and_return_user_credentials(testcase):
    user = create_user()
    return {
        'username': user.username,
        'password': '1234'  # User contains hashed password only so we should
                            # return it as plain text
    }


def create_article_with_its_owner(testcase):
    owner = create_user()
    testcase.owner = owner
    unpublished = create_unpublished_article(commit=False)
    unpublished.owner = owner
    unpublished.save()
    return {'pk': unpublished.pk}


def get_owner_credentials(testcase):
    return {
        'username': testcase.owner.username,
        'password': '1234'  # User contains hashed password only
    }


class UnpublishedArticleSmokeTestCase(SmokeTestCase):
    TESTS_CONFIGURATION = (
        ('articles:article', 404, 'GET',
            {'url_kwargs': create_article_without_owner,
             'comment': 'Anonymous access to unpublished article.'}),  # 1

        ('articles:article', 404, 'GET',
            {'url_kwargs': create_article_without_owner,
             'user_credentials': create_and_return_user_credentials,
             'comment': 'Some user access to unpublished article.'}),  # 2

        ('articles:article', 200, 'GET',
            {'url_kwargs': create_article_with_its_owner,
             'user_credentials': get_owner_credentials,
             'comment': 'Owner access to unpublished article.'}),  # 3
    )
