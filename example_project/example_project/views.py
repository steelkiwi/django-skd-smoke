# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.http import HttpResponse, HttpResponseForbidden, \
    HttpResponseNotFound

from django.views.generic import View


class IsAuthenticated(View):
    """
    If user is authenticated returned 200, else 403.
    """
    def get(self, request, *args, **kwargs):
        if request.user.is_authenticated():
            return HttpResponse()
        else:
            return HttpResponseForbidden()


class OnlyPOSTRequest(View):
    http_method_names = ['post']


class NonExistentURL(View):

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound()
