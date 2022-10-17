from django.contrib import admin
from .models import Client, Master, Visit

# Register your models here.
admin.site.register(Master)


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('visit_date', 'status', 'service_price', 'client', 'master', 'total', 'review', 'rating')
    list_filter = ('visit_date', 'status', 'client')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'client_type')
