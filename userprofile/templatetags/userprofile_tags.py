# -*- coding: utf-8 -*-
from django import template
from django.template.loader import get_template
from userprofile.models import Cooperative
register = template.Library()

@register.inclusion_tag('userprofile/user_box.html')
def user_box(user):
    return { 'user' : user, }

@register.inclusion_tag('userprofile/cooperative_homepage_links.html')
def cooperative_homepage_links():
    return {'cooperatives':Cooperative.objects.all()}

class IfUserIsCoopAdminNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        user_v = template.Variable('user')
        coop_v = template.Variable('cooperative')
        user = user_v.resolve(context)
        if user.is_anonymous():
            return self.nodelist_false.render(context)
        cooperative = coop_v.resolve(context)
        if cooperative in user.get_profile().admin_of_cooperatives.all():
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)

@register.tag()
def if_user_is_coop_admin(parser, token):
    """
    Outputs the contents of the block only if the user is an admin for the
    co-op specified in the domain
    """
    nodelist_true = parser.parse(('else', 'endif_user_is_coop_admin'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endif_user_is_coop_admin',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    return IfUserIsCoopAdminNode(nodelist_true, nodelist_false)


class IfUserIsCoopMemberNode(template.Node):
    def __init__(self, nodelist_true, nodelist_false):
        self.nodelist_true = nodelist_true
        self.nodelist_false = nodelist_false

    def render(self, context):
        user_v = template.Variable('user')
        coop_v = template.Variable('cooperative')
        user = user_v.resolve(context)
        if user.is_anonymous():
            return self.nodelist_false.render(context)
        cooperative = coop_v.resolve(context)
        if cooperative in user.get_profile().cooperatives.all():
            return self.nodelist_true.render(context)
        else:
            return self.nodelist_false.render(context)

@register.tag()
def if_user_is_coop_member(parser, token):
    """
    Outputs the contents of the block only if the user is an member of the
    co-op specified in the domain
    """
    nodelist_true = parser.parse(('else', 'endif_user_is_coop_member'))
    token = parser.next_token()
    if token.contents == 'else':
        nodelist_false = parser.parse(('endif_user_is_coop_member',))
        parser.delete_first_token()
    else:
        nodelist_false = template.NodeList()
    return IfUserIsCoopMemberNode(nodelist_true, nodelist_false)

