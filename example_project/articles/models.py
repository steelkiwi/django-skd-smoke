# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse
from django.db import models


class Article(models.Model):
    headline = models.CharField(max_length=150)
    description = models.TextField(blank=True)

    def __unicode__(self):
        return self.headline

    def get_absolute_url(self):
        return reverse('articles:article', kwargs={'pk': self.pk})
