from django.contrib import admin
from .models import Client, Master, Visit


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('user', 'qualification')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'client_type')


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('visit_date', 'status', 'service', 'client', 'master', 'total', 'review', 'rating')
    list_filter = ('visit_date', 'status', 'client')
