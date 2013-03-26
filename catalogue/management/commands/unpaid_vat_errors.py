from django.core.management.base import NoArgsCommand
from catalogue.models import Catalogue, Order, SumaProduct
from decimal import Decimal
import math

class Command(NoArgsCommand):
    help = "One-off script to work out how much VAT has been underpaid due " + \
           "to vat having not been added in the last order"

    def handle_noargs(self, *args, **kwargs):
        unpaid_vat = {}
        correct_cat = Catalogue.objects.get(ref="May2011-corrected")
        order = Order.objects.get(id=19)
        for basket in order.basket_set.all():
            username = basket.userprofile.user.username
            unpaid_vat[username] = 0
            for basket_item in basket.basketitem_set.all():
                product_code = basket_item.product.supplier_product_code
                correct_prod = SumaProduct.objects.get(catalogue=correct_cat, supplier_product_code=product_code)
                if basket_item.product.is_splittable():
                    basket_price = math.ceil(100*float(basket_item.product.gross_price) / basket_item.product.outgoingUnitsPerIncomingUnit)/100
                    correct_price = math.ceil(100*float(correct_prod.gross_price) / basket_item.product.outgoingUnitsPerIncomingUnit)/100
#                    print basket_item, basket_price, correct_price
                else:
                    basket_price = basket_item.product.gross_price
                    correct_price = correct_prod.get_price()
                unpaid_vat_on_item = (float(correct_price) - float(basket_price)) * basket_item.quantity
                # ignore *overpaid* vat as we've calculated that elsewhere
                if unpaid_vat_on_item > 0:
                    unpaid_vat[username] += unpaid_vat_on_item
                    print basket_item, basket_price, correct_price, "diff:", unpaid_vat_on_item


        print
        print "Totals"
        print "======"
        for k, v in unpaid_vat.items():
            if v:
                print k, v

        print
        print "TOTAL:",sum(unpaid_vat.values())
