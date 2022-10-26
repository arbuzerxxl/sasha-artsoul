from django.contrib import admin
from .models import Calendar, Client, Master, Visit


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('user', 'qualification')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'client_type')


@admin.register(Calendar)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('date_time', 'master', 'is_free')


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('visit', 'status', 'service', 'client', 'total', 'review', 'rating')
    list_filter = ('visit', 'status', 'client')

    def delete_queryset(self, request, queryset):

        for item in queryset:
            item.visit.is_free = True
            item.visit.save()

        queryset.delete()

    def delete_model(self, request, obj):

        obj.delete()
