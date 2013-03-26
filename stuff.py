# -*- coding: utf-8 -*-
from django.conf import settings
from django.shortcuts import get_object_or_404
from django.utils.http import urlquote
from django.http import HttpResponseRedirect
from django.core.exceptions import PermissionDenied, ImproperlyConfigured
from catalogue.models import Cooperative, Order

"""
def get_object_or_none(klass, *args, **kwargs): 
    try: 
        return klass._default_manager.get(*args, **kwargs) 
    except klass.DoesNotExist: 
        return None 
"""

def user_is_coop_admin(view_func):
    """
    Decorator to check the user is an admin of the co-op specified as the subdomain of the url
    """
    def f(request, *args, **kwargs):
        if request.cooperative and request.user.is_authenticated():
            if request.cooperative in request.user.get_profile().admin_of_cooperatives.all():
                return view_func(request, *args, **kwargs)
        path = urlquote(request.get_full_path())
        return HttpResponseRedirect('%s?next=%s' % (settings.LOGIN_URL, path))
    return f

def user_is_coop_member(view_func):
    """
    Decorator to check the user is a member of the co-op specified as the subdomain of the url
    """
    def f(request, *args, **kwargs):
        if request.cooperative and request.user.is_authenticated():
            if request.cooperative in request.user.get_profile().cooperatives.all():
                return view_func(request, *args, **kwargs)
        path = urlquote(request.get_full_path())
        return HttpResponseRedirect('%s?next=%s' % (settings.LOGIN_URL, path))
    return f

def order_is_open(view_func):
    """
    Decorator to check the order specified in the functions args is open
    """
    def f(*args, **kwargs):
        if 'order_id' in args:
            order_id = args['order_id']
        elif 'order_id' in kwargs:
            order_id = kwargs['order_id']
        else:
            raise ImproperlyConfigured("Invalid use of order_is_open.")
        order = get_object_or_404(Order, id=order_id)
        if not order.is_open():
            raise PermissionDenied("Sorry, the order you were trying to access is closed.")
        return view_func(*args, **kwargs)
    return f

