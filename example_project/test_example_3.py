# -*- coding: utf-8 -*-
from __future__ import unicode_literals

# add to readme starting from:
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
