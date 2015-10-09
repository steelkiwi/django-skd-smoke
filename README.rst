================
django-skd-smoke
================

.. image:: https://travis-ci.org/steelkiwi/django-skd-smoke.svg
    :target: https://travis-ci.org/steelkiwi/django-skd-smoke

.. image:: https://coveralls.io/repos/steelkiwi/django-skd-smoke/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/steelkiwi/django-skd-smoke?branch=master

.. image:: https://img.shields.io/pypi/l/django-skd-smoke.svg
    :target: https://pypi.python.org/pypi/django-skd-smoke

.. image:: https://img.shields.io/pypi/v/django-skd-smoke.svg
    :target: https://pypi.python.org/pypi/django-skd-smoke

.. image:: https://img.shields.io/pypi/pyversions/django-skd-smoke.svg
    :target: https://pypi.python.org/pypi/django-skd-smoke

This package is intended for simplification of smoke tests creation.

.. contents::

Installation
------------

You can get django-skd-smoke by using pip::

    $ pip install django-skd-smoke


Usage
-----
After installation you should create new ``TestCase`` derived from
``skd_smoke.SmokeTestCase`` and define your smoke tests configuration.
Please review `Examples`_ section which demonstrates different usecases.
They are related to ``example_project`` directory which contains common
django project.


Configuration
-------------
``TESTS_CONFIGURATION`` of your ``TestCase`` should contain tuple/list of
tuples for every request with the next structure:

.. code-block:: python

    (url, status, method, {'comment': None, 'initialize': None,
                           'url_kwargs': None, 'request_data': None,
                           'user_credentials': None, 'redirect_to': None})


.. list-table::
   :widths: 15 80 5
   :header-rows: 1

   * - Parameter
     - Description
     - Required
   * - url
     - plain url or urlname as string
     - Yes
   * - status
     - expected http status code (200, 404, etc.) as ``int``
     - Yes
   * - method
     - http request method (GET, POST, etc.) as string
     - Yes
   * - comment
     - string which is added to ``__doc__`` of generated test method
     - No
   * - initialize
     - callable object to do any required initialization
     - No
   * - url_kwargs
     - dict or callable object which returns kwargs dict to resolve url using ``django.shortcuts.resolve_url``
     - No
   * - request_data
     - dict or callable object which returns dict to pass it into http method request
     - No
   * - user_credentials
     - dict or callable object which returns dict to login user using ``django.test.TestCase.client.login``
     - No
   * - redirect_to
     - plain url as string which is checked if only status is one of the next: 301, 302, 303, 307
     - No

**NOTE!** All callables take your ``TestCase`` as the first argument so
you can use it to transfer state between them. But take into account that
**order of callbacks usage** is next:

#. ``initialize``
#. ``url_kwargs``
#. ``user_credentials``
#. ``request_data``


Examples
--------

All examples are taken from ``example_project`` package and can be run after
repository cloning.

\1. Demonstration of simple requests:
    1. GET 200
    2. GET 200 with request_data as dict
    3. POST 200
    4. POST 302 with request_data as callable
    5. GET 302 (unauthorized access)
    6. GET 200 (authorized access)
    7. POST 405 (method not allowed)

.. code-block:: python

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


2. Usage of ``initialize`` callback to create several objects to test objects
list.

Suppose you want to make smoke test for articles list page but initially your
test db does not contain any. You can use ``initialize`` callback here to
create several articles.

.. code-block:: python

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

3. Usage of ``redirect_to`` setting to test anonymous access of login required
pages.


.. code-block:: python

    from django.core.urlresolvers import reverse

    from skd_smoke import SmokeTestCase


    class RedirectToSmokeTestCase(SmokeTestCase):
        TESTS_CONFIGURATION = (
            ('is_authenticated', 302, 'GET', {
                'redirect_to': '%s?next=%s' % (reverse('login'),
                                               reverse('is_authenticated')),
                'comment': 'Anonymous profile access with check of redirect url'
            }),
        )

4. Usage of ``url_kwargs`` and ``user_credentials`` callbacks to test
authorized access of owner to newly created object.

Suppose you have a model Article which unpublished version can be viewed by
its owner only. You can test this situation by creating of user in
``url_kwargs`` callback and transfering user to ``user_credentials`` callback.
Unfortunately, you cannot get password from user model cause it contains
hashed password. So you should return password as plain text.

Lets smoke test two other situations when 404 page is showed. Finally we have
three testcases:

i. Anonymous access should show 404 page.
ii. Some ordinary user access should also show 404 page.
iii. Only owner access returns actual article with status 200.

.. code-block:: python

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

License
-------

MIT
