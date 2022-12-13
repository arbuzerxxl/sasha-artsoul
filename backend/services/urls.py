from django.urls import path
from .views import index, my_view, create_calendar, add_users, add_old_calendar, search_client

urlpatterns = [
    path('', index, name='index'),
    path('create_calendar/', create_calendar, name='create_calendar'),
    path('add_old_calendar/', add_old_calendar, name='add_old_calendar'),
    path('search_client/', search_client, name='search_client'),
    path('add_users/', add_users, name='add_users'),
    path('request/login/', my_view, name='req_login'),
    
    
]
