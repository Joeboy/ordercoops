# -*- coding: utf-8 -*-
from django.http import HttpResponse, HttpResponseRedirect
from django.core.cache import cache
from django.shortcuts import render_to_response, get_object_or_404
from django.db import connection
import json
from catalogue.models import ProductCategory, SumaProduct, BasketItem, Basket, Catalogue, Order
from userprofile.models import UserProfile
from django.core.paginator import QuerySetPaginator, InvalidPage
from django.template import RequestContext
from django.db.models import Q
from ordercoops.stuff import user_is_coop_member, order_is_open
import os
from urllib import urlencode

class JsonResponse(HttpResponse):
    def __init__(self, content, mimetype='application/json', status=None, content_type=None):
        super(JsonResponse, self).__init__(
            content=json.dumps(content),
            mimetype=mimetype,
            status=status,
            content_type=content_type,
        )

def make_querystring(url_params):
    """ make a url out of a dict of params,
        remove any empty params """
    params_filtered = dict([i for i in url_params.items() if i[1]])
    return urlencode(params_filtered)
#    return urlencode(params_filtered).replace('&', '&amp;')

def fetch_http_param(request, name, default=None):
    if request.method=='POST':
        return request.POST.get(name, default)
    else:
        return request.GET.get(name, default)


@order_is_open
@user_is_coop_member
def browse(request, order_id):
    order = get_object_or_404(Order, id=order_id)
    Product = order.get_product_model()
    try:
        paginate_by=int(fetch_http_param(request, 'paginate_by', 25))
    except ValueError:
        raise Http404
    try:
        page_number = int(fetch_http_param(request, 'page', 1))
    except ValueError:
        raise Http404
    search = fetch_http_param(request, 'search', None)
    just_basket = fetch_http_param(request, 'just_basket', None)
    just_splittables = fetch_http_param(request, 'just_splittables', None)
    brand_slug = fetch_http_param(request, 'brand', None)
    code = fetch_http_param(request, 'code', None)
    productCategory_slug = request.GET.get('productCategory', None)
    productCategory_slug = fetch_http_param(request, 'productCategory', None)
    try:
        productCategory = ProductCategory.objects.get(slug=productCategory_slug, catalogue=order.catalogue)
    except ProductCategory.DoesNotExist:
        productCategory = None

    kwargs={'catalogue':order.catalogue}
    if brand_slug:
        kwargs['brand_slug'] = brand_slug
    if productCategory:
        kwargs['category'] = productCategory
    if code:
        kwargs['supplier_product_code__istartswith']=code
    if search:
        searchBits=search.split()
    else: searchBits=[]

    if just_basket:
        # This is probably a bit crap:
        basket_item_ids = [i.product.id for i in request.user.get_profile().basket_set.get(order=order).basketitem_set.all()]
        if basket_item_ids:
            filteredProducts = Product.objects.filter(id__in=basket_item_ids)
        else:
            filteredProducts = Product.objects.exclude(id__gt=0)
    else:
        filteredProducts = Product.objects.filter(**kwargs)

    for s in searchBits:
        filteredProducts = filteredProducts.filter(Q(name__icontains=s) | Q(category__name__icontains=s) | Q(brand_name__icontains=s))
    if just_splittables:
        filteredProducts = filteredProducts.filter(outgoingUnitsPerIncomingUnit__gte=2)
    paginator = QuerySetPaginator(filteredProducts, paginate_by)

    page = paginator.page(page_number)

    url_params = { 'brand': brand_slug,
              'productCategory':productCategory_slug,
              'code':code,
              'search':search,
              'paginate_by':str(paginate_by),
              'just_basket':just_basket,
              'page':str(page_number),
              }
    current_url = request.path+'?'+make_querystring(url_params)
    url_params['page'] = str(page_number-1)
    previous_url = request.path+'?'+make_querystring(url_params)
    url_params['page'] = str(page_number+1)
    next_url = request.path+'?'+make_querystring(url_params)

    brands = cache.get('catalogue_%d_brands' % order.catalogue.id)
    if not brands:
        # Refresh brands list...
        cursor = connection.cursor()
        cursor.execute("""select brand_slug, brand_name from catalogue_baseproduct where brand_slug != '' and catalogue_id=%s group by brand_slug, brand_name order by brand_name""", (order.catalogue.id,))

        brands = cursor.fetchall()
        cache.set('catalogue_%d_brands' % order.catalogue.id, brands, 60*60*24*1)

    return render_to_response('catalogue/browse.html', {
            'order' : order,
            'productCategories' : ProductCategory.objects.filter(catalogue=order.catalogue),
            'productCategory' : productCategory,
            'brand' : brand_slug,
            'brands' : brands,
            'search' : search,
            'paginator' : paginator,
            'page': page,
            'next_url':next_url,
            'previous_url':previous_url,
            'current_url':current_url,
            'code' : code,
            'just_basket' : just_basket,
            'total_basket_price':total_basket_price(request.user.username, order.id),
    }, context_instance=RequestContext(request) )

def total_basket_price(username, order_id):
    try:
        userprofile = UserProfile.objects.get(username=username)
    except UserProfile.DoesNotExist:
        return 0
    try:
        basket = userprofile.basket_set.get(order__id=order_id)
    except Basket.DoesNotExist:
        basket = Basket.objects.create(userprofile=userprofile, order_id=order_id)
        basket.save()
    return basket.total_price()

@order_is_open
@user_is_coop_member
def basket_contents_json(request, order_id):
    userprofile = request.user.get_profile()
    items = BasketItem.objects.filter(basket__userprofile = userprofile, basket__order__id=order_id)

    basket_contents = {'items':[{'id':str(i.product.id), 'description':str(i.product.name), 'quantity':str(i.quantity), 'size':str(i.product.get_outgoing_unit_size()), 'total':"%.2f" % (i.quantity*i.product.get_price()),'code':str(i.product.supplier_product_code)} for i in items], 'total_basket_price':"%.2f" % (total_basket_price(userprofile.username, order_id)),}
    return JsonResponse(basket_contents)

@order_is_open
@user_is_coop_member
def amend_basket_quantity(request, order_id, product_id, increment, new_value=None, ajax=True):
    """ ajaxy thing  - add or remove items from basket"""
    userprofile = request.user.get_profile()
    order = get_object_or_404(Order, id=order_id)
    Product = order.get_product_model()
    increment=int(increment)
    new_value = new_value and int(new_value)
    
    product = get_object_or_404(Product, id=product_id)
    try:
        item = BasketItem.objects.get(basket__order__id=order_id, basket__userprofile=userprofile, product=product)
    except BasketItem.DoesNotExist:
        item = None

    if item:
        if increment >0 or increment <0:
            item.quantity+=increment
        else:   
            item.quantity = new_value
        if item.quantity>0:
            item.save()
        else:
            item.delete()
    elif increment>0 or (increment == 0 and new_value > 0):
        basket = Basket.objects.get(userprofile__id=userprofile.id, order__id=order_id)
        item = BasketItem.objects.create(basket=basket, product=product, quantity=increment or new_value)
        item.save()
    if ajax:
        return JsonResponse("success")
    else:
        from urllib import unquote
        return HttpResponseRedirect(unquote(request.GET.get('next')))


#@user_is_staff
#def list_splittable_items(request):
#    return HttpResponse('<br />\n'.join([x.__str__() for x in Product.objects.filter(outgoingUnitsPerIncomingUnit__isnull=False)]))
#
#@user_is_staff
#def toggle_ordering(request):
#    path = os.path.join(os.path.dirname((__file__)), 'ordering_enabled')
#    ordering_enabled=get_ordering_status()
#    if ordering_enabled:
#        f = open(path, 'w')
#        f.write('disabled')
#        f.close()
#    else:
#        f = open(path, 'w')
#        f.write('enabled')
#        f.close()
#    return HttpResponseRedirect('/admin/')

#from catalogue.management import SPLITTABLE_ITEMS
#def split_items_temp(request):
#    # Just a temporary hack...
#    for i in SPLITTABLE_ITEMS:
#        p = get_object_or_none(Product, code=i[0])
#        if p:
#            p.outgoingUnitSize = i[1]
#            p.outgoingUnitsPerIncomingUnit = i[2]
#            p.save()
#    return HttpResponse('Done')

