# -*- coding: utf-8 -*-
from django import template
from django.template import resolve_variable
from catalogue.models import BasketItem

register = template.Library()

class NumInBasketNode(template.Node):
    def __init__(self, product, user):
        self.product = product
        self.user=user

    def render(self, context):
        user = resolve_variable(self.user, context)
        if user.is_anonymous():
            return ''
        userprofile = user.get_profile()
        order = resolve_variable('order', context)  
        product  = resolve_variable(self.product, context)
        try:
            b = BasketItem.objects.get(product__id=product.id, basket__userprofile=userprofile, basket__order=order)
        except BasketItem.DoesNotExist:
            return '0'
        return str(b.quantity) or '0'

def do_num_in_basket(parser, token):
    """ use like {% num_in_basket product user %} """
    bits = token.split_contents()
    return NumInBasketNode(bits[1], bits[2])
register.tag('num_in_basket', do_num_in_basket)


class ItemTotalPriceNode(template.Node):
    def __init__(self, product, user):
        self.product = product
        self.user=user

    def render(self, context):
        user = resolve_variable(self.user, context)
        if user.is_anonymous():
            return ''
        userprofile = user.get_profile()
        order = resolve_variable('order', context)  
        product  = resolve_variable(self.product, context)
        try:
            b = BasketItem.objects.get(product__id=product.id, basket__userprofile=userprofile, basket__order=order)
        except BasketItem.DoesNotExist:
            return '0'
        if b.quantity and product.gross_price:
            return str("%.2f" % (b.quantity * product.get_price(),))
        else:
            return '0'

def do_item_total_price(parser, token):
    """ use like {% item_total_price product user %} """
    bits = token.split_contents()
    return ItemTotalPriceNode(bits[1], bits[2])
register.tag('item_total_price', do_item_total_price)

#class ToggleOrderingStatusNode(template.Node):
#    def render(self, context):
#        from ordercoops.catalogue.views import get_ordering_status
#        if get_ordering_status():
#            return 'Ordering is enabled. <a href="/admin/toggle-ordering/">Click here</a> to disable it.</p>'
#        else:
#            return 'Ordering is disabled. <a href="/admin/toggle-ordering/">Click here</a> to enable it.</p>'
#
#def do_toggle_ordering_status(parser, token):
#    """ use like {% item_total_price product user %} """
#    return ToggleOrderingStatusNode()
#register.tag('toggle_ordering_status', do_toggle_ordering_status)
#
#def entitizeampersands(value):
#    """convert &s to &amp;s (for urls)"""
#    return value.replace('&', '&amp;')
#
#register.filter('entitizeampersands', entitizeampersands)
#
