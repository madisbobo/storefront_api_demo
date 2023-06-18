from django.urls import path
from rest_framework_nested import routers
from . import views

# Router
router = routers.DefaultRouter()
router.register('products', viewset=views.ProductViewSet, basename='products')
router.register('collections', viewset=views.CollectionViewSet, basename='collections')

products_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
products_router.register('reviews', views.ReviewViewSet, basename='product-review')

# URLConf
urlpatterns = router.urls + products_router.urls


# urlpatterns = [
#     router.pat
#     # path('products/', views.ProductList.as_view()), # as_view() converts it into a regular function_based view
#     # path('products/<int:pk>/', views.ProductDetail.as_view()),
#     # path('collections/', views.CollectionList.as_view()),
#     # path('collections/<int:pk>', views.CollectionDetail.as_view())
# ]
