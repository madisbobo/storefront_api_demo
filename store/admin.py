from typing import Any, List, Optional, Tuple
from django.contrib import admin, messages
from django.db.models.query import QuerySet
from django.http.request import HttpRequest
from django.db.models.aggregates import Count
from django.utils.html import format_html, urlencode
from django.urls import reverse
from . import models


# Custom filters
class InventoryFilter(admin.SimpleListFilter):
    title = 'inventory'
    parameter_name = 'inventory'

    # Define the filters
    def lookups(self, request: Any, model_admin: Any) -> List[Tuple[Any, str]]:
        return [
            ('<10', 'Low'),
            ('0', 'Out of Stock')
        ]
    
    # Check if the filter '<10' is selected, return a query with a filter of inventory lt=10
    def queryset(self, request: Any, queryset: QuerySet[Any]) -> QuerySet[Any] | None:
        if self.value() == '0':
            return queryset.filter(inventory=0)
        if self.value() == '<10': 
            return queryset.filter(inventory__lt=10)
        

# # Register your models here (cheap and simple, customization needs to be done via model Meta class)
# admin.site.register(models.Collection)
# admin.site.register(models.Product, ProductAdmin)

# # Register your models here with decorator and customization
@admin.register(models.Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ['title', 'products_count']
    search_fields = ['title']

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
    # Adding a new product - customizing fields
    # fields = ['title', 'slug']
    # exclude = ['promotions']
    # readonly_fields = ['title']
    prepopulated_fields = {
        'slug': ['title']
    }
    autocomplete_fields = ['collection']

    actions = ['clear_inventory']
    list_display = ['title', 'unit_price', 'inventory_status', 'collection_title']
    list_editable = ['unit_price']
    list_filter = ['collection', 'last_update', InventoryFilter]
    list_per_page = 20
    list_select_related = ['collection']
    search_fields = ['title']

    # Adding computed column and sorting
    @admin.display(ordering='inventory')
    def inventory_status(self, product):
        if product.inventory == 0:
            return 'Out of Stock'
        elif product.inventory < 10:
            return 'Low'
        return 'OK'
    
    # Adding related objects
    def collection_title(self, product):
        return product.collection.title
    
    # Defining custom action
    @admin.action(description='Clear inventory')
    def clear_inventory(self, request, queryset):
        updated_count = queryset.update(inventory=0) # returns the number of updated records
        self.message_user(
            request,
            f'{updated_count} products were successfully updated',
            messages.SUCCESS
        )



@admin.register(models.Customer)
class CustomerAdmin(admin.ModelAdmin):
    list_display = ['first_name', 'last_name', 'membership', 'orders_count']
    list_editable = ['membership']
    list_per_page = 20
    ordering = ['first_name', 'last_name']
    search_fields = ['first_name__istartswith', 'last_name__istartswith']

    @admin.display(ordering='orders_count')
    def orders_count(self, customer):
        url = (
            reverse('admin:store_order_changelist')
            + '?'
            + urlencode({'customer__id': str(customer.id)
        }))
        return format_html('<a href="{}">{}</a>', url, customer.orders_count)
        #return customer.orders_count

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(orders_count=Count('order'))


class OrderItemInline(admin.TabularInline):
    autocomplete_fields = ['product']
    min_num = 1
    max_num = 10
    model = models.OrderItem
    extra = 1 # rows

@admin.register(models.Order)
class OrderAdmin(admin.ModelAdmin):
    autocomplete_fields = ['customer']
    inlines = [OrderItemInline]
    list_display = ['id', 'placed_at', 'customer']
    list_per_page = 20
    list_select_related = ['customer']
    ordering = ['id']


