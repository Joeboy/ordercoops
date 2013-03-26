from django.forms import ModelForm
from django import forms
from django.db import connection
from django.template import RequestContext, Context
from django.template.loader import get_template
from django.shortcuts import render_to_response, get_object_or_404
from django.http import HttpResponseRedirect, HttpResponse
from django.core.exceptions import PermissionDenied
from django.core.mail import send_mass_mail
from django.contrib import messages
from catalogue.models import Order, BasketItem, BaseProduct, Catalogue
from userprofile.models import UserProfile
from ordercoops.stuff import user_is_coop_admin
from django.conf import settings

#@user_is_coop_admin
#def home(request):
#    c = RequestContext(request)
#    return object_list(request, queryset = Order.objects.filter(cooperative = c['cooperative']), template_name="catalogue/admin/coop-admin-home.html")
    
class OrderForm(ModelForm):
    class Meta:
        model = Order
        exclude=('cooperative',)

    class Media:
        js=('js/jquery-ui-1.7.1.custom.min.js',)
        css={'screen':('jquery-ui-css/jquery-ui-1.7.1.custom.css',)}

@user_is_coop_admin
def delete_order(request, order_id):
    context = RequestContext(request)
    if request.GET.get('confirm')=='yes':
        order = get_object_or_404(Order, id=order_id)
        order.delete()
        messages.add_message(request, messages.INFO, "Order deleted.")
        return HttpResponseRedirect('/')
    elif request.GET.get('confirm')=='no':
        messages.add_message(request, messages.INFO, "Order deletion cancelled.")
        return HttpResponseRedirect('/')
    else:
        return render_to_response('catalogue/admin/confirm_delete_order.html', context_instance=context)

@user_is_coop_admin
def edit_order(request, order_id=None):
    context = RequestContext(request)
    if request.method == 'POST':
        if order_id:
            order = get_object_or_404(Order, id=order_id)
            form = OrderForm(request.POST, instance=order)
            action="edited"
        else:
            form = OrderForm(request.POST)
            action="created"
        if form.is_valid():
            order = form.save(commit=False)
            order.cooperative = context['cooperative']
            order.save()
            messages.add_message(request, messages.INFO, "Order successfully %s." % action)
            return HttpResponseRedirect('/')
    else:
        if order_id:
            form = OrderForm(instance=get_object_or_404(Order, id=order_id))
        else:
            form = OrderForm()
    return render_to_response('catalogue/admin/edit_order.html', {'form': form}, context)

@user_is_coop_admin
def order_uncollated(request, order_id):
    order_by = request.GET.get('order_by')
    if order_by and order_by == 'product':
        basketItems = BasketItem.objects.filter(basket__order__id=order_id).select_related().all().order_by('catalogue_baseproduct.supplier_product_code',)
    else:
        order_by = 'person'
        basketItems = BasketItem.objects.filter(basket__order__id=order_id).select_related().order_by('catalogue_basket.userprofile_id',)
    if request.GET.get('download'):
        t = get_template("catalogue/admin/order_everyone_csv.html")
        context = Context({'items':basketItems, 'order_by':order_by})
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=order-everyone.csv'
        response.write(t.render(context))
        return response
    else:
        return render_to_response('catalogue/admin/order_everyone.html', {'items':basketItems, 'order_by':order_by})

@user_is_coop_admin
def order_collated(request, order_id):
    cursor = connection.cursor()
    # Get a list of the ids and quantities ordered of products in the order
    cursor.execute("""select product_id, sum(quantity) as outgoing_units from catalogue_basketitem where basket_id in (select id from catalogue_basket where order_id=%s) group by product_id""" % order_id)
    data = []
    grand_total=0
    for r in cursor.fetchall():
        product = BaseProduct.objects.get(id=r[0])
        if product.outgoingUnitsPerIncomingUnit:
            x, y = divmod(r[1], product.outgoingUnitsPerIncomingUnit)
            units_required = x + (y and 1 or 0)
            if y:
                surplus_units = product.outgoingUnitsPerIncomingUnit - y
            else:
                surplus_units = 0
        else:
            units_required = r[1]
            surplus_units = None
        cost = units_required * product.gross_price
        data.append ({'product':product, 'outgoing_units':r[1], 'units_required':units_required, 'surplus_units':surplus_units, 'cost':cost})
        grand_total += cost
#    data = []
#    grand_total=0
#    cursor.execute("""select max(product_id) from catalogue_basketitem where basket_id in (select id from catalogue_basket where order_id=%s) group by product_id""" % order_id)
#    for (product_id,) in cursor.fetchall():
#        units_required=0
#        cost=0
#        for item in BasketItem.objects.filter(product__id=product_id, basket__order__id=order_id):
#            units_required += item.quantity
##        if item.product.is_splittable():
##            surplus_units = num_outgoing_units % item.product.outgoingUnitsPerIncomingUnit
##            incoming_units_required = math.ceil(float(num_outgoing_units) / float(item.product.outgoingUnitsPerIncomingUnit))
##            surplus_units = incoming_units_required * float(item.product.outgoingUnitsPerIncomingUnit) - float(num_outgoing_units)
##        else:
##        surplus_units = 0
##        incoming_units_required = num_outgoing_units
#
##        surplus_units_cost = surplus_units * item.product.get_price()
#        cost=float(item.product.gross_price) * units_required
#        
#        grand_total += cost
#        data.append({'product':item.product, 'units_required':units_required, 'cost':cost,})
    
    if request.GET.get('download'):
        t = get_template("catalogue/admin/order_collated_csv.html")
        context = Context({'data':data, 'grand_total':grand_total})
        response = HttpResponse(mimetype='text/csv')
        response['Content-Disposition'] = 'attachment; filename=order-collated.csv'
        response.write(t.render(context))
        return response
    else:
        return render_to_response('catalogue/admin/order_collated.html', {'data':data, 'grand_total':grand_total})

@user_is_coop_admin
def members(request):
    c = RequestContext(request)
    return render_to_response('catalogue/admin/members.html', {'members':c['cooperative'].userprofile_set.all()}, c)

class MemberForm(ModelForm):
    class Meta:
        model = UserProfile
        exclude=('cooperatives','admin_of_cooperatives')

@user_is_coop_admin
def edit_member(request, userprofile_id=None):
    context = RequestContext(request)
    if request.method == 'POST':
        if userprofile_id:
            userprofile = get_object_or_404(UserProfile, id=userprofile_id)
            form = MemberForm(request.POST, instance=userprofile)
            action="edited"
        else:
            form = MemberForm(request.POST)
            action="created"
        if form.is_valid():
            userprofile = form.save(commit=True)
            if not userprofile_id:
                userprofile.cooperatives = [context['cooperative'],]
                userprofile.admin_of_cooperatives = []
            userprofile.save()
            messages.add_message(request, messages.INFO, "Member successfully %s." % action)
            return HttpResponseRedirect('/coop-admin/members/')
    else:
        if userprofile_id:
            form = MemberForm(instance=get_object_or_404(UserProfile, id=userprofile_id))
        else:
            form = MemberForm()
    return render_to_response('userprofile/edit_userprofile.html', {'form': form}, context)

@user_is_coop_admin
def delete_member(request, userprofile_id):
    context = RequestContext(request)
    if request.GET.get('confirm')=='yes':
        userprofile = get_object_or_404(UserProfile, id=userprofile_id)
        userprofile.delete()
        messages.add_message(request, messages.INFO, "Member deleted.")
        return HttpResponseRedirect('/coop-admin/members/')
    elif request.GET.get('confirm')=='no':
        messages.add_message(request, messages.INFO, "Member deletion cancelled.")
        return HttpResponseRedirect('/coop-admin/members/')
    else:
        return render_to_response('userprofile/confirm_delete_member.html', context_instance=context)

class EmailMembersForm(forms.Form):
    subject = forms.CharField(max_length=100)
    message = forms.CharField(widget=forms.Textarea)

@user_is_coop_admin
def email_all(request):
    context = RequestContext(request)
    if request.method == 'POST':
        form = EmailMembersForm(request.POST)
        if form.is_valid():
            send_mass_mail( [  ( form.cleaned_data['subject'],
                                 form.cleaned_data['message'],
                                 request.user.email,
                                 [u.user.email for u in context['cooperative'].userprofile_set.all()]),
                            ],
                            auth_user=settings.SMTP_USERNAME, auth_password=settings.SMTP_PASSWORD)
            messages.add_message(request, messages.INFO, "Email sent.")
            return HttpResponseRedirect('/')
    else:
        form = EmailMembersForm()
    return render_to_response('catalogue/admin/email_all_members.html', {'form': form}, context)

class EditHomepageTextForm(forms.Form):
    text = forms.CharField(widget=forms.Textarea)

@user_is_coop_admin
def edit_homepage(request):
    context = RequestContext(request)
    if request.method == 'POST':
        form = EditHomepageTextForm(request.POST)
        if form.is_valid():
            context['cooperative'].homepage_text = form.cleaned_data['text']
            context['cooperative'].save()
            messages.add_message(request, messages.INFO, "Homepage text changed.")
            return HttpResponseRedirect('/')
    else:
        form = EditHomepageTextForm({'text':context['cooperative'].homepage_text})

    return render_to_response('catalogue/admin/edit_homepage.html', {'form': form}, context)

class CatalogueForm(forms.ModelForm):
    class Meta:
        model = Catalogue
        exclude = ('data_import_completed',)

    class Media:
        js=('js/jquery-ui-1.7.1.custom.min.js',)
        css={'screen':('jquery-ui-css/jquery-ui-1.7.1.custom.css',)}

def upload_catalogue(request):
    if not request.user.is_staff:
        raise PermissionDenied
    if request.POST:
        form = CatalogueForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return HttpResponseRedirect('/catalogue/upload-done/')
    else:
        form = CatalogueForm()

    context = RequestContext(request)
    return render_to_response('catalogue/admin/upload_catalogue.html', {'form': form}, context)

def upload_catalogue_done(request):
    return render_to_response('catalogue/admin/upload_catalogue_done.html')
