# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf import settings
from django.core.urlresolvers import reverse
from django.db import models


class Article(models.Model):
    headline = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    published = models.BooleanField(default=True)
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, blank=True, null=True)

    def __unicode__(self):
        return self.headline

    def get_absolute_url(self):
        return reverse('articles:article', kwargs={'pk': self.pk})
