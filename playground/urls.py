from django.urls import path
from . import views

# URLConf
urlpatterns = [
    path('hello/', views.say_hello),
    path('slow-hello/', views.slow_hello),
    path('class-slow-hello/', views.HelloView.as_view())
]

