from django.urls import path
from .views import index, my_view, create_calendar

urlpatterns = [
    path('', index, name='index'),
    path('create_calendar/', create_calendar, name='create_calendar'),
    path('request/login/', my_view, name='req_login'),
]
