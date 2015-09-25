# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.core.urlresolvers import reverse_lazy
from django.http import HttpResponse, HttpResponseNotFound
from django.views.generic import View, TemplateView
from django.contrib.auth.decorators import login_required
from django.utils.decorators import method_decorator


class LoginRequiredMixin(object):
    @method_decorator(login_required(login_url=reverse_lazy('login')))
    def dispatch(self, request, *args, **kwargs):
        return super(LoginRequiredMixin, self).dispatch(
            request, *args, **kwargs)


class IsAuthenticated(LoginRequiredMixin, TemplateView):

    def get(self, request, *args, **kwargs):
        return HttpResponse()


class OnlyPOSTRequest(View):
    http_method_names = ['post']

    def post(self, request, *args, **kwargs):
        return HttpResponse()


class NonExistentURL(View):

    def get(self, request, *args, **kwargs):
        return HttpResponseNotFound()

    def post(self, request, *args, **kwargs):
        return HttpResponseNotFound()
