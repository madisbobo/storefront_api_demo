from django.contrib import admin
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models


# # Register your models here (cheap and simple, customization needs to be done via model Meta class)
# admin.site.register(models.Collection)
# admin.site.register(models.Product, ProductAdmin)

# # Register your models here with decorator and customization
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']

    @admin.display(ordering='products_count')
    def products_count(self, collection):
        url = (
            reverse('admin:store_product_changelist')
            + '?'
            + urlencode({
               'collection__id': str(collection.id) 
            }))
        return format_html('<a href="{}">{}</a>', url, collection.products_count) # Provide a link to other pages
        # return collection.products_count
    
    # Override the base queryset
    def get_queryset(self, request):
        return super().get_queryset(request).annotate(products_count=Count('product'))


@admin.register(models.Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_filter = ['collection', 'last_update']
    list_per_page = 20
    list_select_related = ['collection']

# Register your models here.
