# -*- coding: utf-8 -*-
from django.shortcuts import render_to_response
from django.contrib.auth import authenticate, login, logout
from django.template import RequestContext
from django.http import HttpResponseRedirect
from catalogue.models import Basket

def user_login(request):
    if request.user.is_authenticated():
        return render_to_response('userprofile/login-form.html', {'alreadyloggedin':True,}, context_instance=RequestContext(request))
    if request.POST:
        user = authenticate(username=request.POST['username'], password=request.POST['password'])
        if user is not None:
            if request.cooperative in user.get_profile().cooperatives.all():
                login(request, user)
                if request.POST.has_key('next'):
                    return HttpResponseRedirect(request.POST['next'])
                else:
                    return HttpResponseRedirect('/user/logged-in/')
            else:
                return render_to_response('userprofile/failed-login-wrong-coop.html', context_instance=RequestContext(request))
        else:
            return render_to_response('userprofile/failed-login.html', context_instance=RequestContext(request))
    else:
        return render_to_response('userprofile/login-form.html', context_instance=RequestContext(request, {'next':request.GET['next'],}))

def user_logout(request):
    if request.method=='GET':
        next=request.GET.get('next')
    elif request.method=='POST':
        next=request.POST.get('next')
    next = next or '/user/logged-out/'
    if request.user.is_authenticated():
        logout(request)
        return HttpResponseRedirect(next)
    else:
        return HttpResponseRedirect(next)

def user_logged_in(request):
    try:
        from smartpages.models import SmartPage
    except ImportError:
        return render_to_response('userprofile/logged_in.html', context_instance=RequestContext(request))
    try:
        sp = SmartPage.objects.get(slug='logged-in')
        return render_to_response('smartpages/default.html', {'content':sp.content}, context_instance=RequestContext(request))
    except SmartPage.DoesNotExist:
        return render_to_response('userprofile/logged_in.html', context_instance=RequestContext(request))
    
def user_logged_out(request):
    try:
        from smartpages.models import SmartPage
    except ImportError:
        return render_to_response('userprofile/logged_out.html', context_instance=RequestContext(request))
    try:
        sp = SmartPage.objects.get(slug='logged-out')
        return render_to_response('smartpages/default.html', {'content':sp.content}, context_instance=RequestContext(request))
    except SmartPage.DoesNotExist:
        return render_to_response('userprofile/logged_out.html', context_instance=RequestContext(request))
    
