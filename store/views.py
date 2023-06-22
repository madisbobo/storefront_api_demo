from django.db.models.aggregates import Count
from django.shortcuts import render, get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.permissions import IsAuthenticated, AllowAny, IsAdminUser
from rest_framework.decorators import action
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.response import Response
from rest_framework import status
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, UpdateModelMixin
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from .pagination import DefaultPagination
from .permissions import IsAdminOrReadOnly, ViewCustomerHistoryPermission
from .filters import ProductFilter
from .models import Product, Collection, OrderItem, Review, Cart, CartItem, Customer
from .serializers import ProductSerializer, CollectionSerializer, ReviewSerializer, CartSerializer, CartItemSerializer, AddCartItemSerializer, UpdateCartItemSerializer, CustomerSerializer


# # Unused imports, which we used earlier
# from django.http import HttpResponse
# from rest_framework.views import APIView
# from rest_framework.mixins import CreateModelMixin, ListModelMixin
# from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
# from rest_framework.decorators import api_view


# Create your views here.


## --- VIEW SETS --- ##
# # ViewSets combine the functionality of multiple individual views into a single class, 
# # making it easier to manage and maintain your API code. They are especially useful when 
# # dealing with resources that have standard CRUD (Create, Retrieve, Update, Delete) operations.



class ProductViewSet(ModelViewSet):
    queryset = Product.objects.all()
    serializer_class = ProductSerializer
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter] # Filtering using DjangoFilterBackend
    # If no custom filter needed, use filterset_fields = ['collection_id'] # Filtering using DjangoFilterBackend
    filterset_class = ProductFilter
    pagination_class = DefaultPagination
    permission_classes = [IsAdminOrReadOnly]
    search_fields = ['title', 'description']
    ordering_fields = ['unit_price', 'last_update']

    def get_serializer_context(self):
        return {'request': self.request} ## Find out
    
    def destroy(self, request, *args, **kwargs):
        if OrderItem.objects.filter(product_id=kwargs['pk']).count() > 0:
            return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)
    
    # Filtering logic built manually
    # def get_queryset(self):
    #     queryset = Product.objects.all()
    #     collection_id = self.request.query_params.get('collection_id')
    #     if collection_id is not None:
    #         queryset = queryset.filter(collection_id=collection_id)
    #     return queryset


class CollectionViewSet(ModelViewSet):
    queryset = Collection.objects.annotate(product_count=Count('products'))
    serializer_class = CollectionSerializer
    permission_classes = [IsAdminOrReadOnly]

    def destroy(self, request, *args, **kwargs):
        if Product.objects.filter(collection_id=['pk']).count() > 0:
            return Response({'error': 'Collection cannot be deleted because it is associated with one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
        return super().destroy(request, *args, **kwargs)


class ReviewViewSet(ModelViewSet):
    serializer_class = ReviewSerializer

    def get_queryset(self):
        return Review.objects.filter(product_id=self.kwargs['product_pk'])

    def get_serializer_context(self):
        return {'product_id': self.kwargs['product_pk']}


class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items__product').all()
    serializer_class = CartSerializer

class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        elif self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('product')
    
    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk']}


class CustomerViewSet(ModelViewSet):
    queryset = Customer.objects.all()
    serializer_class = CustomerSerializer
    permission_classes = [IsAdminUser]

    # "action" refers to a custom, non-standard endpoint or operation that you can define within a viewset or a class-based view. Actions provide additional functionalities beyond the default CRUD operations (Create, Retrieve, Update, Delete) associated with RESTful APIs.
    @action(detail=False, methods=['GET', 'PUT'], permission_classes=[IsAuthenticated]) # If false, the action will be available on a list view
    def me(self, request):
        # request.user - If user not loggid in, this will be set to an instance of AnonymousUser class, otherwise userobject
        (customer, created) = Customer.objects.get_or_create(user_id=request.user.id)
        if request.method == 'GET':
            serializer = CustomerSerializer(customer)
            return Response(serializer.data)
        elif request.method == 'PUT':
            serializer = CustomerSerializer(customer, data=request.data)
            serializer.is_valid(raise_exception=True)
            serializer.save()
            return Response(serializer.data)

    @action(detail=True, permission_classes=[ViewCustomerHistoryPermission])
    def history(self, request, pk):
        return Response('OK')








""" 
    SERVICE                     |    METHOD    |    URL                  |    REQUEST          |    RESPONSE
    --------------------------------------------------------------------------------------------------------
    Create a cart               |    POST      | /carts/                 |  {}                 |    cart (object)
    Get a cart with its items   |    GET       | /carts/:id              |  {}                 |    cart 
    Delete a cart               |    DELETE    | /carts/:id              |  {}                 |    {} 
    Add items to a cart         |    POST      | /carts/:id/items        |  {productId, qty}   |    item
    Update the quantity of items|    PATCH     | /carts/:id/items/:id    |  {qty}              |    {qty}
    Remove items from a cart    |    DELETE    | /carts/:id/items/:id    |  {}                 |    {}

"""


""" 
    SERVICE                     |    METHOD    |    URL                  |    REQUEST          |    RESPONSE       |    PERMISSIONS
    --------------------------------------------------------------------------------------------------------------------------------
    Create an order             |    POST      | /orders/                |  {cartId}           |    order (object) | only for authenticated users (userId sent via JWT header)
    Get all order               |    GET       | /orders/                |  {}                 |    order[]        | only my own orders or admin can see everything
    Get a specific order        |    GET       | /orders/:id/            |  {}                 |    order          | only my own orders or admin can see everything
    Update an order             |    PATCH     | /orders/:id/            |  {}                 |    order          | Admin only
    Delete an order             |    DELETE    | /orders/:id/            |  {}                 |    order          | Admin only

"""

# Context object is used to provide additional information to the serializer

## --- GENERIC VIEWS --- ##
# # In Django, generic views are pre-built class-based views provided by the Django framework. They offer 
# # a convenient and reusable way to handle common patterns and functionalities in web development, 
# # such as displaying lists of objects, creating new objects, updating existing objects, and deleting objects.

## MIXINS ## 
# # In Django, mixins are a way to provide reusable functionality to class-based views or class-based models. 
# # Mixins are essentially classes that define specific behaviors or functionalities that can be combined with 
# # other classes using multiple inheritance. Mixins are useful when you want to reuse code across multiple 
# # views or models without the need for code duplication.

# class ProductList(ListCreateAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def get_serializer_context(self):
#         return {'request': self.request}


# class ProductDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Product.objects.all()
#     serializer_class = ProductSerializer

#     def delete(self, request, pk):
#         product = get_object_or_404(Product, pk=pk)
#         if product.orderitems.count() > 0:
#             return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# class CollectionList(ListCreateAPIView):
#     queryset = Collection.objects.annotate(product_count=Count('products'))
#     serializer_class = CollectionSerializer

# class CollectionDetail(RetrieveUpdateDestroyAPIView):
#     queryset = Collection.objects.annotate(product_count=Count('products'))
#     serializer_class = CollectionSerializer

#     def delete(self, request, pk):
#         collection = get_object_or_404(Collection.objects.annotate(product_count=Count('products')), pk=pk)
#         if collection.products.count() > 0:
#             return Response({'error': 'Collection cannot be deleted because it is associated with one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response({"message": "Collection deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


## --- CLASS-BASED VIEWS --- ##

# class ProductList(APIView):
#     def get(self, request):
#         queryset = Product.objects.all()
#         # queryset = Product.objects.select_related('collection').all() # In order to get the collections for Seralizing Relationships using StringField
#         serializer = ProductSerializer(queryset, many=True, context={'request': request})
#         return Response(serializer.data)
    
#     def post(self, request):
#         serializer = ProductSerializer(data=request.data) # ProductSerializer is going to deseriazlise the data. If the data is valid, the serializer creates a new instance of the Product model object with the deserialized data.
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
        

# class ProductDetail(APIView):
#     def get(self, request):
#         product = get_object_or_404(Product, pk=id)
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)
    
#     def put(self, request):
#         product = get_object_or_404(Product, pk=id)
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
    
#     def delete(self, request):
#         product = get_object_or_404(Product, pk=id)
#         if product.orderitems.count() > 0:
#             return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# class CollectionList(APIView):
#     def get(self, request):
#         queryset = Collection.objects.annotate(product_count=Count('products'))
#         serializer = CollectionSerializer(queryset, many=True)
#         return Response(serializer.data)

#     def post(self, request):
#         serializer = CollectionSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)


# class CollectionDetail(APIView):
#     def get(self, request, id):
#         collection = get_object_or_404(Collection.objects.annotate(product_count=Count('products')), pk=id)
#         serializer = CollectionSerializer(collection)
#         return Response(serializer.data)
    
#     def put(self, request, id):
#         collection = get_object_or_404(Collection.objects.annotate(product_count=Count('products')), pk=id)
#         serializer = CollectionSerializer(collection, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)

#     def delete(self, request, id):
#         collection = get_object_or_404(Collection.objects.annotate(product_count=Count('products')), pk=id)
#         if collection.products.count() > 0:
#             return Response({'error': 'Collection cannot be deleted because it is associated with one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response({"message": "Collection deleted successfully"}, status=status.HTTP_204_NO_CONTENT)



## __________________________________________________________ ##

# # --- FUNCTION BASED VIEW --- # #
# @api_view(['GET', 'POST'])
# def product_list(request):
#     if request.method == 'GET':
#         queryset = Product.objects.all()
#         # queryset = Product.objects.select_related('collection').all() # In order to get the collections for Seralizing Relationships using StringField
#         serializer = ProductSerializer(queryset, many=True)
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer = ProductSerializer(data=request.data) # ProductSerializer is going to deseriazlise the data. If the data is valid, the serializer creates a new instance of the Product model object with the deserialized data.
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

# @api_view(['GET', 'PUT', 'DELETE'])
# def product_detail(request, id):
#     # Get the product object (row)
#     product = get_object_or_404(Product, pk=id)
#     if request.method == 'GET':    
#         # Serializer converts a model instance to a dictionary (Like a DTO)
#         serializer = ProductSerializer(product)
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = ProductSerializer(product, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == 'DELETE':
#         if product.orderitems.count() > 0:
#             return Response({'error': 'Product cannot be deleted because it is associated with an order item.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         product.delete()
#         return Response({"message": "Product deleted successfully"}, status=status.HTTP_204_NO_CONTENT)

# @api_view(['GET', 'POST'])
# def collection_list(request):
#     if request.method == 'GET':
#         queryset = Collection.objects.annotate(product_count=Count('products'))
#         serializer = CollectionSerializer(queryset, many=True)
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer = CollectionSerializer(data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)

# @api_view(['GET', 'PUT', 'DELETE'])
# def collection_detail(request, id):
#     collection = get_object_or_404(Collection.objects.annotate(product_count=Count('products')), pk=id)
#     if request.method == 'GET':
#         serializer = CollectionSerializer(collection)
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = CollectionSerializer(collection, data=request.data)
#         serializer.is_valid(raise_exception=True)
#         serializer.save()
#         return Response(serializer.data)
#     elif request.method == 'DELETE':
#         if collection.products.count() > 0:
#             return Response({'error': 'Collection cannot be deleted because it is associated with one or more products.'}, status=status.HTTP_405_METHOD_NOT_ALLOWED)
#         collection.delete()
#         return Response({"message": "Collection deleted successfully"}, status=status.HTTP_204_NO_CONTENT)


# _______ ##
    # # With Try and Except
    # try:
    #     # Get the product object (row)
    #     product = Product.objects.get(pk=1)
    #     # Serializer converts a model instance to a dictionary (Like a DTO)
    #     serializer = ProductSerializer(product)
    #     return Response(serializer.data)
    # except Product.DoesNotExist:
    #     return Response(status=status.HTTP_404_NOT_FOUND)
    
    


# In Django REST Framework, there's a class called JSONRenderer, which takes a dictionary and turns it into a JSON object