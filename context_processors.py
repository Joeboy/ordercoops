# -*- coding: utf-8 -*-
from userprofile.models import Cooperative
from django.http import Http404

def coop_subdomain(request):
    return {'cooperative':request.cooperative}

