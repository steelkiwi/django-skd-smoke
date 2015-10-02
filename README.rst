================
django-skd-smoke
================

.. image:: https://travis-ci.org/steelkiwi/django-skd-smoke.svg
    :target: https://travis-ci.org/steelkiwi/django-skd-smoke

.. image:: https://coveralls.io/repos/steelkiwi/django-skd-smoke/badge.svg?branch=master&service=github
    :target: https://coveralls.io/github/steelkiwi/django-skd-smoke?branch=master

This package is intended for simplification of smoke tests creation.

Installation
============

You can get django-skd-smoke by using pip::

    $ pip install https://github.com/steelkiwi/django-skd-smoke/archive/master.zip


Usage
=====
After installation you should create new `TestCase` derived from
`skd_smoke.SmokeTestCase` and define your smoke tests configuration.


Configuration
=============
`TESTS_CONFIGURATION` of your `TestCase` should contain tuple/list of tuples
with the next structure:

.. code-block:: python

    (url, status, method, {'initialize': None, 'get_url_kwargs': None,
                           'request_data': None,'get_user_credentials': None})

+---------------------+-------------------------------------------+-----------+
|   Parameter         | Description                               | Required  |
+=====================+===========================================+===========+
| url                 | plain url or urlname                      | Yes       |
+---------------------+-------------------------------------------+-----------+
| status              | http status code (200, 404, etc.)         | Yes       |
+---------------------+-------------------------------------------+-----------+
| method              | http request method (GET, POST, etc.)     | Yes       |
+---------------------+-------------------------------------------+-----------+
| initialize          | callable to do any required initialization| No        |
+---------------------+-------------------------------------------+-----------+
| get_url_kwargs      | callable to specify `kwargs` for urlname  | No        |
+---------------------+-------------------------------------------+-----------+
| request_data        | data dict which is used as GET/POST data  | No        |
+---------------------+-------------------------------------------+-----------+
| get_user_credentials| callable -> {'username':'', 'password':''}| No        |
+---------------------+-------------------------------------------+-----------+

All callables take generated ``TestCase`` as the first argument in order to
store inside it some variables (i.e. user).

Example
=======

1. Usage of `get_url_kwargs` and `get_user_credentials` callbacks to test
authorized access of owner to newly created object.

.. code-block:: python

    from django.contrib.auth import get_user_model

    from skd_smoke import SmokeTestCase

    from ..models import SomeObject

    def create_object(self):
        UserModel = get_user_model()
        new_user = UserModel.objects.create(username='test_user')
        new_user.set_password('1234')
        new_user.save()
        self.user = new_user
        new_object = SomeObject.objects.create(owner=new_user)
        return {'pk': new_object.pk}

    def get_user_credentials(self):
        return {'username': self.user.username, 'password': '1234'}


    class YourSmokeTests(SmokeTestCase):
        TESTS_CONFIGURATION = (
            ('url', 200, 'GET',
                {'get_url_kwargs': create_object,
                 'get_user_credentials': get_user_credentials}),
        )


