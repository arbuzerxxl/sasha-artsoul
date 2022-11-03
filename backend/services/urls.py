from django.urls import path
from .views import index, my_view

urlpatterns = [
    path('', index, name='index'),
    path('request/login/', my_view, name='req_login'),
]
