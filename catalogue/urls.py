from django.conf.urls import *
#from catalogue.views import get_ordering_status

urlpatterns = patterns('',
#    (r'^orders/$', 'ordercoops.catalogue.admin_views.list_orders'),
    (r'^orders/new/$', 'ordercoops.catalogue.admin_views.edit_order'),
    (r'^orders/edit/(?P<order_id>[\d]+)/$', 'ordercoops.catalogue.admin_views.edit_order'),
    (r'^upload/$', 'ordercoops.catalogue.admin_views.upload_catalogue'),
    (r'^upload-done/$', 'ordercoops.catalogue.admin_views.upload_catalogue_done'),
)
 
