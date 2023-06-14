from django.shortcuts import render
from django.http import HttpResponse # query expression; reference a particular field
from django.db.models import Q, F, Value, Func, ExpressionWrapper, DecimalField
from django.db.models.functions import Concat
from django.db.models.aggregates import Count, Max, Min, Avg, Sum
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

    # # Customers with .com email account
    # queryset = Customer.objects.filter(email__iendswith='.com')

    # Products with low inventory (less than 10)
    qs_low_inventory_products = Product.objects.filter(
        inventory__lt=10).order_by('-inventory')

    # # Collections that don't have a featured product
    # collections_no_featured_product = Collection.objects.filter(featured_product_id__isnull=True)

    # # Orders placed by customer with id=1
    # customer_1_orders = Order.objects.filter(customer_id=1)

    # # Order items for products in collection 3
    # order_items_c3 = OrderItem.objects.filter(product_collection_id=3)

    # # Products: inventory < 10 AND price < 20
    # queryset = Product.objects.filter(invetory__lt=10, unit_price__lt=20)

    # # Products: inventory < 10 AND price < 20 (chain the call to filter method)
    # queryset = Product.objects.filter(invetory__lt=10).filter(unit_price__lt=10)

    # ----------- Q AND F Objects ---------- #
    # # Products: inventory < 10 OR price < 20 (using Q objects)
    # queryset = Product.objects.filter(Q(inventory__lt=10) | Q(unit_price__lt=20))

    # # Products: inventory < 10 AND price not < 20 (using Q objects)
    # queryset = Product.objects.filter(Q(inventory__lt=10) & ~Q(unit_price__lt=20))

    # # Products: inventory = price
    # queryset = Product.objects.filter(inventory=F('price'))

    # ----------- SORTING ---------- #
    # # Sorting table ASC
    # queryset = Product.objects.order_by('title')

    # # Sorting table ASC, DESC
    # queryset = Product.objects.order_by('unit_price', '-title')

    # # Filter by collection ID and sort by unit price
    # queryset = Product.objects.filter(collection_id=1).order_by('unit_price')
    # most_expensive_product = Product.objects.order_by('-unit_price')[0]
    # most_expensive_product = Product.objects.order_by('-unit_price').first
    # most_expensive_product = Product.objects.earliest('-unit_price')
    # most_expensive_product = Product.objects.latest('unit_price')

    # ----------- LIMITING RESULTS ---------- #
    # queryset = Product.objects.all()[0:5]

    # ----------- SELECTING FIELDS TO QUERY ---------- #
    # # Selecting id title and collection id. Returns a dictionary of objects
    # queryset = Product.objects.values('id', 'title', 'collection__title')

    # # Selecting id title and collection id. Returns a tuble of objects
    # queryset = Product.objects.values_list('id', 'title', 'collection__title')

    # # Select products that have been ordered and sort them by title (ASC)
    # queryset = OrderItem.objects.values('product_id', 'product__title').distinct().order_by('product__title')

    # # Alternative method: Select products that have been ordered and sort them by title (ASC)
    # queryset = Product.objects.filter(id__in=OrderItem.objects.values('product_id').distinct()).order_by('title')

    # # ----------- SELECTING RELATED OBJECTS ---------- #
    # # When we use select_related method, Django create a join between our tables, thus allowing to easily render another table
    # # Use select_related (1) when the other end of the relationship has one instance (e.g. product has one collection)
    # # Use prefetch_related when the other end of the relationship has many objects (e.g. product has many promotions)
    # queryset = Product.objects.select_related('collection').all()
    # queryset = Product.objects.prefetch_related('promotions').all()
    # queryset = Product.objects.prefetch_related('promotions').select_related('collection').all()

    # # Get the last 5 orders with their customer and items (incl product)
    queryset = OrderItem.objects.select_related('order').select_related(
        'order__customer', 'product').order_by('-order__placed_at')[:5]
    # # Alternative: queryset = Order.objects.select_related('customer').prefetch_related('orderitem_set__product').order_by('-placed_at')[0:5]
    
    # # ----------- AGGREGATE METHODS ---------- #
    result = Product.objects.filter(collection__id=3).aggregate(count=Count('id'), min_price=Min('unit_price'))
    # How many orders do we have?
    orders_count = Order.objects.aggregate(total_orders=Count('id'))
    # How many units of product 1 have we sold?
    product_1 = Product.objects.filter(id=1).values('title')[0]['title']
    units_sold = OrderItem.objects.filter(product_id=1).aggregate(sum=Sum('quantity'))
    # How many orders has customer 1 placed?
    customer_1 = Customer.objects.filter(id=1).values('first_name', 'last_name')[0]
    orders_by_c1 = Order.objects.filter(customer_id=1).aggregate(count=Count('id'))
    # What is the min, max and average price of the products in collection 3?
    collection_3 = Collection.objects.filter(id=3).values('title')[0]['title']
    collection_3_pricing = Product.objects.filter(collection_id=3).aggregate(
        min_price=Min('unit_price'),
        max_price=Max('unit_price'),
        avg_price=Avg('unit_price')
    )

    # # ----------- ANNOTATING OBJECTS ---------- #
    # # To add additional attributes to an object (additional column to a table) when quering them
    # # Use Funct to write any SQL functions, e.g. CONCAT 
    # queryset = Customer.objects.annotate(is_new=Value('True')) # Cannot pass boolean, that's why we use Value expression object
    # queryset = Customer.objects.annotate(new_id = F('id') + 1)
    # queryset_2 = Customer.objects.annotate(
    #     full_name=Func(F('first_name'), Value(' '), F('last_name'), function='CONCAT')
    # )
    # # Alternative for Func you can use Django built in Concat function (Django database function)
    # queryset_2 = Customer.objects.annotate(full_name=Concat('first_name', Value(' '), 'last_name'))
    # queryset_2 = Customer.objects.annotate(orders_count=Count('order')) 

    # # Need to use the ExpressionWrapper to specify the output_field (decimal and float are used in an expression)
    # discounted_price = ExpressionWrapper(F('unit_price') * 0.8, output_field=DecimalField())
    # queryset_2 = Product.objects.annotate(discounted_price=discounted_price)

    # # Customers with their last order ID
    # queryset_2 = Customer.objects.annotate(last_order_ID=Max('order__id'))
    # # Collections and count of their products
    # queryset_2 = Collection.objects.annotate(products_count=Count('product__id'))
    # Customers with more than 5 orders
    # queryset_2 = Customer.objects.annotate(orders_count=Count('order__id')).filter(orders_count__gt=5)
    # Customers and the total amount they’ve spent
    # queryset_2 = Customer.objects.annotate(total_spend=Sum(F('order__orderitem__unit_price') * F('order__orderitem__quantity')))
    # Top 5 best-selling products and their total sales
    queryset_2 = Product.objects.annotate(total_sales=Sum(F('orderitem__unit_price') * F('orderitem__quantity'))).order_by('-total_sales')[:5]


    return render(reuqest, 'hello.html', {
        'name': 'Madis',
        'orders': list(queryset),
        'result': result,
        'orders_count': orders_count,
        'units_sold': units_sold,
        'product_1': product_1,
        'customer_1': customer_1,
        'orders_by_c1': orders_by_c1,
        'collection_3': collection_3,
        'collection_3_pricing': collection_3_pricing,
        'low_inventory_products': list(qs_low_inventory_products),
        'funct_query': list(queryset_2)})
