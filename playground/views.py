from django.shortcuts import render
from django.http import HttpResponse
from django.core.exceptions import ObjectDoesNotExist
from store.models import Customer, Product, Order, Collection, OrderItem

# Create your views here. It like a controller in Java, request handler (takes request and returns a response)

def say_hello(reuqest):    
    # # Boolean
    # exists = Product.objects.filter(pk=0).exists()

    # # Try / Except
    # try:
    #     product = Product.objects.get(pk = 0)
    # except ObjectDoesNotExist:
    #     pass

    # # Filter
    # product = Product.objects.filter(pk=0).first()
    
    # # keyword=value (__gt = greater than)
    # queryset = Product.objects.filter(unit_price__gt=20)

    # # keyword __range
    # queryset = Product.objects.filter(unit_price__range=(20,30))

    # # Search for product by title (i makse it case insensitive). You also have title__startswith, __endswith, etc.
    # queryset = Product.objects.filter(title__icontains='coffee')

    # # for dates, you can use year, month, date, etc.
    # queryset = Product.objects.filter(last_update__year=2021)

    # # to get all products where description is null
    # queryset = Product.objects.filter(description__isnull=True)

    # Customers with .com email account
    queryset = Customer.objects.filter(email__iendswith='.com')

    # Products with low inventory (less than 10)
    qs_low_inventory_products = Product.objects.filter(inventory__lt=10).order_by('-inventory')

    # # Collections that don't have a featured product
    # collections_no_featured_product = Collection.objects.filter(featured_product_id__isnull=True)

    # # Orders placed by customer with id=1
    # customer_1_orders = Order.objects.filter(customer_id=1)

    # # Order items for products in collection 3
    # order_items_c3 = OrderItem.objects.filter(product_collection_id=3)

    return render(reuqest, 'hello.html', {
        'name': 'Madis', 
        'customers': list(queryset), 
        'low_inventory_products': list(qs_low_inventory_products)})





