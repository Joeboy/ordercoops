from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^members/$', 'catalogue.admin_views.members'),
    (r'^members/edit/(?P<userprofile_id>\d+)/$', 'catalogue.admin_views.edit_member'),
    (r'^members/delete/(?P<userprofile_id>\d+)/$', 'catalogue.admin_views.delete_member'),
    (r'^members/new/$', 'catalogue.admin_views.edit_member'),
    (r'^members/email-all/$', 'catalogue.admin_views.email_all'),
    (r'^edit-homepage/$', 'catalogue.admin_views.edit_homepage'),
#    (r'^$', 'catalogue.admin_views.home'),
    (r'^edit-order/(?P<order_id>\d+)/$', 'catalogue.admin_views.edit_order'),
    (r'^new-order/$', 'catalogue.admin_views.edit_order'),
    (r'^delete-order/(?P<order_id>\d+)/$', 'catalogue.admin_views.delete_order'),
    (r'^uncollated-order/(?P<order_id>\d+)/$', 'ordercoops.catalogue.admin_views.order_uncollated'),
    (r'^collated-order/(?P<order_id>\d+)/$', 'ordercoops.catalogue.admin_views.order_collated'),
#    (r'^orders/$', 'ordercoops.catalogue.admin_views.list_orders'),
)
 
