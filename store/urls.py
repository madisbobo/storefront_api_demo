from django.urls import path
from rest_framework_nested import routers
from . import views

# Router
router = routers.DefaultRouter()
router.register('products', viewset=views.ProductViewSet, basename='products')
router.register('collections', viewset=views.CollectionViewSet, basename='collections')
router.register('carts', viewset=views.CartViewSet, basename='carts')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product') # Lookup parameter specifies the keyword argument used for looking up the parent instance.
products_router.register('reviews', views.ReviewViewSet, basename='product-review') # Basename parameter is used to define the base name for the registered viewset. It helps in generating the URL patterns for the viewset's endpoints.

carts_router = routers.NestedDefaultRouter(router,'carts', lookup='cart')
carts_router.register('items', views.CartItemViewSet, basename='cart-item')

# URLConf
urlpatterns = router.urls + products_router.urls + carts_router.urls


# urlpatterns = [
#     router.pat
#     # path('products/', views.ProductList.as_view()), # as_view() converts it into a regular function_based view
#     # path('products/<int:pk>/', views.ProductDetail.as_view()),
#     # path('collections/', views.CollectionList.as_view()),
#     # path('collections/<int:pk>', views.CollectionDetail.as_view())
# ]
