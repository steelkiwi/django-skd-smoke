# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.conf.urls import include, url
from django.contrib import admin
from django.contrib.auth.views import login, logout
from django.views.generic import TemplateView
from articles import urls

from .views import IsAuthenticated, OnlyPOSTRequest, NonExistentURL

urlpatterns = [
    url(r'^admin/', include(admin.site.urls)),
    url(r'^$', TemplateView.as_view(template_name="base.html"), name='home'),
    url(r'^login/$', login, {'template_name': 'login.html'}, name='login'),
    url(r'^logout/$', logout, {'template_name': 'logout.html'}, name='logout'),
    url(r'^is_authenticated/$', IsAuthenticated.as_view(),
        name='is_authenticated'),
    url(r'^only_post_request/$', OnlyPOSTRequest.as_view(),
        name='only_post_request'),
    url(r'^non_existent_url/$', NonExistentURL.as_view(),
        name='non_existent_url'),
    url(r'^articles/', include(urls, namespace='articles'))
]
