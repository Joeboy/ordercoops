from django.conf.urls import *
from django.contrib import admin
admin.autodiscover()
from django.conf import settings

urlpatterns = patterns('',
    url(r'^order-(?P<order_id>\d+)/', include('catalogue.ordering_urls')),
    url(r'^coop-admin/', include('catalogue.coop_admin_urls')),

    url(r'^catalogue/', include('ordercoops.catalogue.urls')),
    url(r'^$', 'ordercoops.views.homepage'),
    url(r'^user/', include('ordercoops.userprofile.urls')),
    url(r'^r/', include('django.conf.urls.shortcut')), # For the 'View on site' button in the admin

#    (r'^admin/user-passwords/$', 'ordercoops.views.user_passwords'),
#    (r'^admin/user-emails/$', 'ordercoops.views.user_emails'),

    url('^admin/', admin.site.urls),
    url(r'^robots.txt$', 'django.views.static.serve', {'document_root': settings.MEDIA_ROOT, 'path':'robots.txt'}),
)
 
