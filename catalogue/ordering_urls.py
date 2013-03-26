from django.conf.urls.defaults import *

urlpatterns = patterns('',
    (r'^browse/$', 'ordercoops.catalogue.views.browse'),
    (r'^amend-basket-quantity/(?P<product_id>[\d]+)/(?P<increment>-?[\d]+)/(?P<new_value>-?[\d]+)/?$', 'ordercoops.catalogue.views.amend_basket_quantity'),
    (r'^amend-basket-quantity/no-ajax/(?P<product_id>[\d]+)/(?P<increment>-?[\d]+)/$', 'ordercoops.catalogue.views.amend_basket_quantity', {'ajax':False,}),
    (r'^basket-contents-json/$', 'ordercoops.catalogue.views.basket_contents_json'),
)
 
