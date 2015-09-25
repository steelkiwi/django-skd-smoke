# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings

SKD_SMOKE_TESTS_CONFIG_MODULE = getattr(
    settings,
    'DJANGO_SKD_SMOKE_TESTS_CONFIG_MODULE',
    'skd_smoke.smoketests_example'
)
