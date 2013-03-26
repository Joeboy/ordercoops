# -*- coding: utf-8 -*-
from django.contrib.auth.models import User, Group
from django.contrib.auth import models as auth_app
from ordercoops.userprofile import models as userprofile_app
from ordercoops.userprofile.models import UserProfile, Cooperative
from django.db.models import signals
from django.db import models
from django.dispatch import dispatcher
from django.db.models.signals import post_syncdb

default_users = [ ('test', 'dummyaddress@example.com', 'test', ('test',), )
                ]

default_cooperatives = ( 'nautia', 'test' )

def bootstrap_users(sender, *args, **kwargs):
    print "Adding default cooperatives..."
    for c in default_cooperatives:
        try:
            d = Cooperative.objects.get(subdomain=c)
        except Cooperative.DoesNotExist:
            d = Cooperative.objects.create(subdomain=c, name=c, homepage_text="<p>Welcome to the %s ordering homepage</p>" % c)
            d.save()

    print "Adding default users..."

    for u in default_users:
        try:
            user = User.objects.get(username=u[0])
            print "(Possibly) modifying user '%s'" % u[0]
        except User.DoesNotExist:
            print "Creating user '%s'" % u[0]
            user = User.objects.create_user(u[0], u[1] or 'unknown@noidea.com', u[2])
        if u[0] == 'test':
            user.is_staff=True
            user.is_superuser=True
        user.save()
        UserProfile.objects.filter(username=u[0]).delete()
        up=UserProfile(
                    username = user.username,
                    name=user.username,
                    user=user,
                    email=user.email,
                    password=u[2],
            )
        up.save()
        up.cooperatives = [Cooperative.objects.get(subdomain=c) for c in u[3]]
        if u[0] == 'test':
            up.admin_of_cooperatives = [Cooperative.objects.get(subdomain='nautia'),]
        up.save()

post_syncdb.connect(bootstrap_users)


