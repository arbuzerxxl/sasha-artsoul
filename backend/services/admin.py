from django.contrib import admin
from .models import Calendar, Client, Master, Visit


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'last_visit_manicure', 'last_visit_pedicure')


@admin.register(Calendar)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('date_time', 'master', 'is_free')


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('calendar', 'status', 'service', 'client', 'total', 'review', 'rating')
    list_filter = ('calendar', 'status', 'client')

    # def save_model(self, request, obj, form, change) -> None:
    #     if obj.calendar is None:
    #         obj.calendar = Visit.objects.get(id=obj.id).calendar
    #     return super().save_model(request, obj, form, change)

    def delete_queryset(self, request, queryset):

        for item in queryset:
            item.calendar.is_free = True
            item.calendar.save()

        queryset.delete()

    def delete_model(self, request, obj):

        obj.delete()
