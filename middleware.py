# -*- coding: utf-8 -*-
from ordercoops.userprofile.models import Cooperative
from django.http import Http404

class SubdomainMiddleware(object):

    def process_request(self, request):#, func, args, kwargs):
        hostname = request.META['HTTP_HOST']
        if hostname.startswith('localhost') or hostname.startswith('ordercoops') or hostname.startswith('www.'):
            request.cooperative = None
        else:
            subdomain = hostname[:hostname.find('.')]
            try:
                request.cooperative = Cooperative.objects.get(name=subdomain)
            except Cooperative.DoesNotExist:
                raise Http404, "Sorry, ain't no such co-operative"
