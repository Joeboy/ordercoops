from django.conf.urls import *

urlpatterns = patterns('',
    (r'^login/$', 'userprofile.views.user_login'),
    (r'^logout/$', 'userprofile.views.user_logout'),
    (r'^logged-out/$', 'userprofile.views.user_logged_out'),
    (r'^logged-in/$', 'userprofile.views.user_logged_in'),
#	(r'^$', 'links.views.index'),
#	(r'^(?P<link_id>\d+)/$', 'links.views.detail'),
) 
