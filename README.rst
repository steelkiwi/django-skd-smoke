================
django-skd-smoke
================

.. image:: https://travis-ci.org/steelkiwi/django-skd-smoke.svg
    :target: https://travis-ci.org/steelkiwi/django-skd-smoke

.. image:: https://coveralls.io/repos/steelkiwi/django-skd-smoke/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/steelkiwi/django-skd-smoke?branch=master

This package is intended for simplification of smoke tests creation.

Installation
------------

You can get django-skd-smoke by using pip::

    $ pip install https://github.com/steelkiwi/django-skd-smoke/archive/master.zip


Usage
-----
After installation you should create new ``TestCase`` derived from
`skd_smoke.SmokeTestCase` and define your smoke tests configuration.
Please review ``example_project`` directory which contains common django
project and demonstrates django-skd-smoke usage.


Configuration
-------------
``TESTS_CONFIGURATION`` of your ``TestCase`` should contain tuple/list of
tuples for every request with the next structure:

.. code-block:: python

    (url, status, method, {'initialize': None, 'url_kwargs': None,
                           'request_data': None,'user_credentials': None})


.. list-table::
   :widths: 15 80 5
   :header-rows: 1

   * - Parameter
     - Description
     - Required
   * - url
     - plain url or urlname as ``basestring``
     - Yes
   * - status
     - http status code (200, 404, etc.) as ``int``
     - Yes
   * - method
     - http request method (GET, POST, etc.) as ``basestring``
     - Yes
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

**NOTE!** All callables take your ``TestCase`` as the first argument so
you can use it to transfer state between them. But take into account that
**order of callbacks usage** is next:

#. ``initialize``
#. ``url_kwargs``
#. ``user_credentials``
#. ``request_data``


Examples
--------

\1. Demonstration of simple requests:
    1. GET 200
    2. GET 200 with request_data as dict
    3. POST 201
    4. POST 201 with request_data as callable
    5. GET 302 (unauthorized access)
    6. GET 200 (authorized access)
    7. POST 405 (method not allowed)

.. code-block:: python

    from django.contrib.auth import get_user_model

    from skd_smoke import SmokeTestCase


    def get_new_object_data(testcase):
        return {'title': 'new object',
                'description': 'detailed object description'}


    def get_user_credentials(testcase):
        UserModel = get_user_model()
        username = 'test_user'
        password = '1234'
        new_user = UserModel.objects.create(username=username)
        new_user.set_password(password)
        new_user.save()
        return {
            'username': username,
            'password': password
        }


    class YourSmokeTests(SmokeTestCase):
        TESTS_CONFIGURATION = (
            ('home', 200, 'GET',),  # 1
            ('home', 200, 'GET', {'request_data': {'scrollTop': 1}} ),  # 2
            ('create', 201, 'POST',),  # 3
            ('create', 201, 'POST', {'request_data': get_new_object_data}),  # 4
            ('profile', 302, 'GET',),  # 5
            ('profile', 200, 'GET', {'user_credentials': get_user_credentials}),  # 6
            ('/post_only/', 405, 'GET',),  # 7
        )


2. Usage of ``initialize`` callback to create several objects to test objects
list.

Suppose you want to make smoke test for model list page. Initially your test db
does not contain any objects. You can use ``initialize`` callback here to
create your objects.


.. code-block:: python

    from skd_smoke import SmokeTestCase

    from ..models import SomeModel


    def create_list(testcase):
        for i in range(3):
            SomeModel.objects.create()


    class YourSmokeTests(SmokeTestCase):
        TESTS_CONFIGURATION = (
            ('somemodel_list', 200, 'GET',
                {'initialize': create_list}  # pass your func here
            ),
        )



3. Usage of ``url_kwargs`` and ``user_credentials`` callbacks to test
authorized access of owner to newly created object.

Suppose you have a model which unpublished version can be viewed by its owner
only. You can test this situation by creating of user in ``url_kwargs``
callback and transfering user to ``user_credentials`` callback.

.. code-block:: python

    from django.contrib.auth import get_user_model

    from skd_smoke import SmokeTestCase

    from ..models import SomeModel

    def create_object(testcase):
        UserModel = get_user_model()
        new_user = UserModel.objects.create(username='test_user')
        new_user.set_password('1234')
        new_user.save()
        testcase.user = new_user
        new_object = SomeModel.objects.create(owner=new_user)
        return {'pk': new_object.pk}

    def get_user_credentials(testcase):
        return {
            'username': testcase.user.username,
            'password': '1234' # User contains hashed password only
        }


    class YourSmokeTests(SmokeTestCase):
        TESTS_CONFIGURATION = (
            ('url', 200, 'GET',
                {'url_kwargs': create_object,
                 'user_credentials': get_user_credentials}),
        )


