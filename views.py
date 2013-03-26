# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.template import RequestContext

#from django.http import HttpResponse
#from userprofile.models import UserProfile
#from suma.stuff import user_is_staff

#@user_is_staff
#def user_emails(request):
#    return HttpResponse(', '.join([u.email_address() for u in UserProfile.objects.order_by('username') if u.email_address()]), mimetype='text/plain')

#@user_is_staff
# Need to fix decorator to user_is_admin_of_coop or something
#def user_passwords(request):
#    return HttpResponse("\n".join(["%s (%s):%s" % (u.name, u.username, u.password) for u in UserProfile.objects.order_by('username')]), mimetype='text/plain')

def homepage(request):
    if request.cooperative:
        return render_to_response('userprofile/cooperative-homepage.html', context_instance = RequestContext(request))
    else:
        return render_to_response('homepage.html', context_instance = RequestContext(request))
