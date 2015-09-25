# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase


class OrdinaryTestCase(TestCase):
    """
    Added just to test that it always runs regardless of skd_smoke tests run
    status.
    """

    def test_home(self):
        self.assertEqual(self.client.get('/').status_code, 200)
