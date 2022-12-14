from django.urls import path
from .views import index, my_view, create_superuser, add_old_clients, add_old_calendar, search_client, create_calendar

urlpatterns = [
    path('', index, name='index'),
    path('create_calendar/', create_calendar, name='create_calendar'),
    path('create_superuser/', create_superuser, name='create_superuser'),
    path('add_old_calendar/', add_old_calendar, name='add_old_calendar'),
    path('search_client/', search_client, name='search_client'),
    path('add_old_clients/', add_old_clients, name='add_old_clients'),
    path('request/login/', my_view, name='req_login'),
]
