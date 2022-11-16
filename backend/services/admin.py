from django.contrib import admin
from .models import Calendar, Client, Master, Visit


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type')


@admin.register(Calendar)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('date_time', 'master', 'is_free')


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('calendar', 'status', 'service', 'client', 'total', 'review', 'rating')
    list_filter = ('calendar', 'status', 'client')

    def delete_queryset(self, request, queryset):

        for item in queryset:
            item.calendar.is_free = True
            item.calendar.save()

        queryset.delete()

    def delete_model(self, request, obj):

        obj.delete()
