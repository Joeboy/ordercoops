# -*- coding: utf-8 -*-
from django.db import models
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.conf import settings

# catch exception to allow module to be loaded when syncdbing
try:
    domain = Site.objects.get(id=settings.SITE_ID).domain
except:
    domain=None

class Cooperative(models.Model):
    subdomain = models.SlugField(max_length=15, unique=True, db_index=True)
    name = models.CharField(max_length=150)
    homepage_text = models.TextField(blank=True)

    def __unicode__(self):
        return "Cooperative: %s" % self.name

    def get_absolute_absolute_url(self):
        """ Include the domain (hence the absolute absoluteness """
        return "http://%s.%s" % (self.subdomain, domain)

    def save(self, *args, **kwargs):
        if not self.homepage_text:
            self.homepage_text="<p>Welcome to the homepage of the <strong>%s</strong> ordering co-operative.</p>" % self.name
        super(Cooperative, self).save(*args, **kwargs)

class UserProfile(models.Model):
    user = models.ForeignKey(User,editable=False)
    name = models.CharField(max_length=100)
    username = models.CharField(max_length=100, unique=True)
    email = models.EmailField()
    password = models.CharField(max_length=100)
    cooperatives = models.ManyToManyField(Cooperative, null=True, blank=True)
    admin_of_cooperatives = models.ManyToManyField(Cooperative, related_name='admin_userprofile_set', null=True, blank=True)

    def __unicode__(self):
        return 'UserProfile: %s (%s)' % (self.username, self.name,)

    def save(self, *args, **kwargs):
        try:
            self.user.username=self.username
            self.user.email=self.email
            self.user.set_password(self.password)
        except User.DoesNotExist:
            self.user=User.objects.create_user(self.username, self.email, self.password)
        self.user.save()
        super(UserProfile,self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        self.user.delete()
        super(UserProfile,self).delete(*args, **kwargs)

    def email_address(self):
        if self.email == 'unknown@noidea.com':
            return None
        return "%s <%s>" % (self.name, self.email)

