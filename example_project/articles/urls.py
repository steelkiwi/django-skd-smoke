# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from articles.views import ArticlesView, ArticleView

urlpatterns = (
    url('^$', ArticlesView.as_view(), name='articles'),
    url('^(?P<pk>[0-9]+)/$', ArticleView.as_view(), name='article'),
)
