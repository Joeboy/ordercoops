from django.core.management.base import NoArgsCommand
from catalogue.models import Order
from decimal import Decimal

class Command(NoArgsCommand):
    help = "One-off script to work out how much VAT has been overpaid due " + \
           "50% VAT having been erroneously applied to 5% VATed items."

    def handle_noargs(self, *args, **kwargs):
        overpayments = {}
        for order in Order.objects.all():
#            print order, order.catalogue
            for basket in order.basket_set.all():
                for item in basket.basketitem_set.all():
#                    print type(item.product)
                    if float(item.product.vat_rate) > 0.15:
                        print item
                        amount_paid =  float(item.product.gross_price) * item.quantity
                        print "amount paid = ", amount_paid
                        correct_amount = float(item.product.net_price) * 1.05 * item.quantity
                        print "correct amount = ", correct_amount
                        overpayment = amount_paid - correct_amount
                        print "overpayment =", overpayment
                        try:
                            overpayments[basket.userprofile.user.username] += overpayment
                        except KeyError:
                            overpayments[basket.userprofile.user.username] = overpayment
        print
        print "Overpayments"
        print "============"
        for k, v in overpayments.items():
            print k, round(v, 2)
