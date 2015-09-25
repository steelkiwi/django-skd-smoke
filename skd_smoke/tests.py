# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.test import TestCase

from . import GenerateTestMethodsMeta


class SmokeTestCase(TestCase):
    __metaclass__ = GenerateTestMethodsMeta
