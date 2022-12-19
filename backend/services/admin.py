from django.contrib import admin
from .models import Calendar, Client, Master, Visit
from datetime import datetime


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'last_visit_manicure', 'last_visit_pedicure')
    # sortable_by = ('user__last_name')


@admin.register(Calendar)
class CalendarAdmin(admin.ModelAdmin):
    list_display = ('date_time', 'master', 'is_free')
    list_filter = ('is_free',)


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('calendar', 'status', 'service', 'client', 'extra_total', 'discount', 'total', 'review', 'rating')
    list_filter = ('calendar__date_time', 'status', 'client')
    search_fields = ('status', 'client__user__last_name', 'calendar__date_time__month')
    sortable_by = ('calendar', 'status',)

    def delete_queryset(self, request, queryset):

        for item in queryset:

            if item.service in [item.Services.CORRECTION, item.Services.BUILD_UP]:
                now = datetime(year=item.calendar.date_time.year,
                               month=item.calendar.date_time.month,
                               day=item.calendar.date_time.day,
                               hour=item.calendar.date_time.hour + 2,
                               minute=item.calendar.date_time.minute)
            try:
                next_calendar_record = Calendar.objects.get(date_time=now)
                next_calendar_record.is_free = True
                next_calendar_record.save()
            except Calendar.DoesNotExist:
                pass

            item.calendar.is_free = True
            item.calendar.save()

        queryset.delete()

    def delete_model(self, request, obj):

        obj.delete()
