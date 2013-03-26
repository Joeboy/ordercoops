from django.contrib import admin
from catalogue.models import (Catalogue, ProductCategory, SumaProduct,
                              Basket, BasketItem, Order)

class SumaProductAdmin(admin.ModelAdmin):
    search_fields = ('supplier_product_code', 'name',)
    list_filter = ('catalogue',)

    def lookup_allowed(self, key, value):
        if key in ('catalogue__id__exact',):
            return True

        return super(SumaProductAdmin, self).lookup_allowed(key)


admin.site.register(Catalogue)
admin.site.register(ProductCategory)
admin.site.register(SumaProduct, SumaProductAdmin)
admin.site.register(Basket)
admin.site.register(BasketItem)
admin.site.register(Order)
