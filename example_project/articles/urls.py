# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import url

from .views import ArticlesView, ArticleDetailView, ArticleCreateView

urlpatterns = (
    url('^$', ArticlesView.as_view(), name='articles'),
    url('^create/$', ArticleCreateView.as_view(), name='create'),
    url('^(?P<pk>[0-9]+)/$', ArticleDetailView.as_view(), name='article'),
)
