# -*- coding: utf-8 -*-
import os, re, csv
import math
from decimal import *
from datetime import datetime, date
from django.db import models, transaction
from django.template.defaultfilters import slugify
from userprofile.models import UserProfile, Cooperative
from ordercoops import settings
VAT_CHOICES = (('V', 'V'), ('5', '5'))
NEW_CHOICES = (('NEW', 'NEW'),)
PRICECHANGE_CHOICES = (('UP', 'UP'), ('DOWN', 'DOWN'))
ONOFFER_CHOICES = (('OFFER', 'OFFER'), ('END', 'END'))
from ordercoops.catalogue.splittable_items import SPLITTABLE_ITEMS

class EssentialProductManager(models.Manager):
    def import_from_textfile(self, filepath, catalogue):
        self.model.objects.filter(catalogue=catalogue).delete()
        csvfile = open(filepath)
        dictreader = csv.DictReader(csvfile, dialect='excel')
        multispace_re = re.compile(' +')
        for row in dictreader:
            row = dict([(k, multispace_re.sub(' ', row[k].strip())) for k in row.keys()])
            if not row['Code']:
                continue
            try:
                c=ProductCategory.objects.get(name=row['Catname'], catalogue=catalogue)
            except ProductCategory.DoesNotExist:
                c = ProductCategory.objects.create(name=row['Catname'], slug=slugify(row['Catname']), catalogue=catalogue)
                c.save()

            if row['Price']:
                net_price=float(row['Price'])
            else:
                net_price=0

            if row['VAT'] == 'V':
                vat_rate = 0.15
            elif row['VAT'] == 'F':
                vat_rate = 0.5
            elif row['VAT'] == 'Z':
                vat_rate = 0
            else:
                raise ValueError("Bad VAT value (%s)" % row['VAT'])

            p = self.model.objects.create(
                catalogue=catalogue,
                supplier_product_code=row['Code'],
                brand_name=row['Origin'],
                brand_slug=slugify(row['Origin']),
                category=c,
                name=row['Description'],
                size=row['Pack_Size'],
                net_price=net_price,
                gross_price=net_price*(1+vat_rate),
                vat_rate=vat_rate,
                organic = row['Org']=='ORG' and True or False,
                fair_trade = row['FT']=='F' and True or False,
                gluten_free = row['GF']=='G' and True or False,
            )
            p.save()
        csvfile.close()
        catalogue.data_import_completed=True
        catalogue.save()

# Suma like to vary the column names in the csv file. This maps names to
# canonical header names:
HEADER_EQUIVS = (
("PLCDE", "PL CODE"),
("PLTEXT", "PL TEXT"),
("FGOSV", "BFGOSV"),
("PLDESC", "DESCRIPTION"),
("NEW CATEGORY", "CATEGORY"),
("ON OFFER?", "ON OFFER"),
)

class SumaProductManager(models.Manager):
    @transaction.commit_on_success
    def import_from_textfile(self, filepath, catalogue):
        SumaProduct.objects.filter(catalogue=catalogue).delete()
        csvfile = open(filepath, 'U')
        headers = [z.strip() for z in csvfile.readline().strip().split('\t')]
        for e, c in HEADER_EQUIVS:
            if e in headers:
                headers[headers.index(e)] = c
        dictreader = csv.DictReader(csvfile, headers, dialect='excel-tab')
        for row in dictreader:
            row = dict([(k, v.strip() if isinstance(v, basestring) else v) for k, v in row.iteritems()])
            if not row['PL CODE']:
                continue
            try:
                c=ProductCategory.objects.get(name=row['CATEGORY'], catalogue=catalogue)
            except ProductCategory.DoesNotExist:
                c = ProductCategory.objects.create(name=row['CATEGORY'], slug=slugify(row['CATEGORY']), catalogue=catalogue)
                c.save()
#            brand=row['BRAND'].
#            try:
#                b = Brand.objects.get(name=brand)
#            except Brand.DoesNotExist:
#                if re.search('\w', brand):
#                    b = Brand.objects.create(name=brand, slug=slugify(brand))
#                    b.save()
#                else:
#                    b=None
            if row['PRICE']=='Discontinued':
                discontinued=True
            else:
                discontinued=False

            if row['PRICE']=='FREE':
                net_price=Decimal(0)
            elif row['PRICE']:
                net_price=Decimal(row['PRICE'])
            else:
                net_price=None

            if row['VAT'] in ('', None):
                vat_rate = Decimal('0')
            elif row['VAT'].lower() == 'v':
                vat_rate = Decimal('0.20')
            else:
                vat_rate = Decimal(row['VAT'])/100
                # If you get an exception here, there's something unexpected
                # in the VAT column.
                 
            p = SumaProduct.objects.create(
                catalogue=catalogue,
                supplier_product_code=row['PL CODE'],
                brand_name=row['BRAND'],
                brand_slug=slugify(row['BRAND']),
                category=c,
                name=row['DESCRIPTION'],
                pl_text=row['PL TEXT'].strip(' '),
                size=row['SIZE'],
                net_price=net_price,
                gross_price=None if net_price is None else net_price*(Decimal(1)+vat_rate),
                vat_rate=vat_rate,
                rrp=row['RRP'] or None,
                bfgosv=row['BFGOSV'],
                new=row['NEW?'] and True or False,
                on_offer=row['ON OFFER'] and True or False,
                normal_price=row['NORMAL PRICE'] or None,
                normal_rrp=row['NORMAL RRP'] or None,        
                discontinued=discontinued,
            )
            p.save()
        csvfile.close()
        catalogue.data_import_completed=True
        catalogue.save()
        for i in SPLITTABLE_ITEMS:
            try:
                p = BaseProduct.objects.get(catalogue=catalogue, supplier_product_code=i[0])
                p.outgoingUnitSize = i[1]
                p.outgoingUnitsPerIncomingUnit = i[2]
                p.save()
            except BaseProduct.DoesNotExist:
                pass
#                print "No such product: %s" % i[0]

class Catalogue(models.Model):
    ref = models.SlugField(unique=True, help_text="eg. Suma, May-June-2008")
    csvfile = models.FileField(upload_to='catalogues')
    start_date = models.DateField(blank=True, null=True)
    expiry_date = models.DateField(blank=True, null=True)
    data_import_completed = models.BooleanField(default=False)
    supplier = models.CharField(max_length=50, choices=(('Suma','Suma'), ('Essential','Essential')))

    def __unicode__(self):
        return "%s - %s" % (self.supplier, self.ref)
#    objects = CatalogueManager()

    def csvfilepath(self):
        return os.path.join(settings.MEDIA_ROOT, self.csvfile.name)

    @transaction.commit_on_success
    def save(self, *args, **kwargs):
        super(Catalogue, self).save(*args, **kwargs)
        # This is quite nasty
        if self.csvfile and not self.data_import_completed:
            globals()['%sProduct' % self.supplier].objects.import_from_textfile(self.csvfilepath(), self)


#class Brand(models.Model):
#    name = models.CharField(max_length=250, unique=True, db_index=True)
#    slug = models.SlugField()
#
#    class Meta:
#        ordering=['name',]
#
#    def __unicode__(self):
#        return self.name
#
class ProductCategory(models.Model):
    name = models.CharField(max_length=250)
    slug = models.SlugField(db_index=True)
    catalogue = models.ForeignKey(Catalogue, db_index=True)

    class Meta:
        ordering=['slug',]
        unique_together = (("name", "catalogue"), ("slug", "catalogue"))

    def __unicode__(self):
        return self.name


class BaseProduct(models.Model):
    """ Base model with some likely common fields """
    catalogue = models.ForeignKey(Catalogue, db_index=True)
    supplier_product_code = models.CharField(max_length=100, db_index=True, blank=True)
    name = models.TextField()
    brand_name = models.CharField(max_length=50, db_index=True)
    brand_slug = models.CharField(max_length=50, db_index=True)
    category = models.ForeignKey(ProductCategory, db_index=True, blank=True, null=True)
    size = models.CharField(max_length=100, blank=True, null=True)
    net_price = models.DecimalField(decimal_places=2, max_digits=6, null=True, blank=True)
    vat_rate = models.DecimalField(decimal_places=4, max_digits=5, default=0)
    gross_price = models.DecimalField(decimal_places=2, max_digits=6, null=False, blank=False)
    # splittable items:
    outgoingUnitSize = models.CharField(max_length=100, null=True, blank=True)
    outgoingUnitsPerIncomingUnit = models.IntegerField(null=True, blank=True)


    def is_splittable(self):
        return self.outgoingUnitsPerIncomingUnit and self.outgoingUnitSize and True

    def get_price(self):
        if self.is_splittable():
            return math.ceil(100*float(self.gross_price) / self.outgoingUnitsPerIncomingUnit)/100
        else:
            return self.gross_price

    def extra_info(self):
        """ override this to show extra info in the catalogue browser """
        return ''

    def get_outgoing_unit_size(self):
        if self.is_splittable():
            return self.outgoingUnitSize
        else:
            return self.size

    class Meta:
#        ordering=['category', 'grossPrice']
        ordering=['supplier_product_code']
#        abstract=True

    def save(self, *args, **kwargs):
        self.gross_price = self.net_price * (Decimal(1)+self.vat_rate)
        super(BaseProduct, self).save(*args, **kwargs)

    def __unicode__(self):
        return "%s: %s (%s)" % (self.supplier_product_code, self.name, self.brand_name and self.brand_name or '')

class EssentialProduct(BaseProduct):
    country = models.CharField(max_length=25, null=True, blank=True)
    organic = models.BooleanField()
    fair_trade = models.BooleanField()
    gluten_free = models.BooleanField()

    objects = EssentialProductManager()

    def extra_info(self):
        return ', '.join([f for f in ('organic', 'fair trade', 'gluten free') if getattr(self, f.replace(' ', '_'))])

    class Meta:
        pass

    def __unicode__(self):
        return "%s: %s %s (%s)" % (self.supplier_product_code, self.name, self.pl_text, self.brand_name and self.brand_name or '')


class SumaProduct(BaseProduct):
    bfgosv = models.CharField(max_length=10, blank=True)
    rrp = models.DecimalField(decimal_places=2, max_digits=6, blank=True, null=True)
    normal_price = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=6)
    normal_rrp = models.DecimalField(blank=True, null=True, decimal_places=2, max_digits=6)
    new = models.BooleanField(default=False)
    on_offer = models.BooleanField()
    discontinued = models.BooleanField()
    pl_text = models.CharField(max_length=250, blank=True)

    objects = SumaProductManager()

    def extra_info(self):
        return self.bfgosv

    class Meta:
        pass

    def __unicode__(self):
        return "%s: %s %s (%s)" % (self.supplier_product_code, self.name, self.pl_text, self.brand_name and self.brand_name or '')

class Order(models.Model):
    cooperative = models.ForeignKey(Cooperative, db_index=True)
    catalogue = models.ForeignKey(Catalogue, db_index=True)
    closing_date = models.DateField()
    delivery_date = models.DateField()
    open = models.BooleanField()

    def is_open(self):
        return self.open and (date.today() <= self.closing_date)

    def __unicode__(self):
        return "%s - %s" % (self.catalogue.supplier, self.delivery_date)

    class Meta:
        ordering = ('closing_date', 'delivery_date', )

    class Admin:
        pass

    def get_product_model(self):
        return globals()['%sProduct' % self.catalogue.supplier]


class Basket(models.Model):
    userprofile = models.ForeignKey(UserProfile, db_index=True)
    order = models.ForeignKey(Order)

    # need a 'current basket' manager...
    class Meta:
        ordering=['userprofile']

    def total_price(self):
        return sum([float(i.quantity * i.product.get_price()) for i in self.basketitem_set.all()])

    def __unicode__(self):
        return "%s's basket" % self.userprofile.name

class BasketItem(models.Model):
    basket = models.ForeignKey(Basket, db_index=True)
    product = models.ForeignKey(BaseProduct, db_index=True)
    quantity = models.IntegerField()

    def __unicode__(self):
        return "%s: %s x%d" % (self.basket.userprofile.username, self.product.name, self.quantity)

    def total_price(self):
        return self.product.get_price() * self.quantity


