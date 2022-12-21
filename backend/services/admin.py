from datetime import datetime
from django.utils import timezone
from django.contrib import admin
from .models import Calendar, Client, Master, Visit


@admin.register(Master)
class MasterAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type')


@admin.register(Client)
class ClientAdmin(admin.ModelAdmin):
    list_display = ('user', 'user_type', 'last_visit_manicure', 'last_visit_pedicure')


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

                local_time = timezone.localtime(item.calendar.date_time)

                next_visit = timezone.make_aware(datetime(year=local_time.year, month=local_time.month, day=local_time.day,
                                                          hour=local_time.hour + 2, minute=local_time.minute))

                try:
                    next_calendar_record = Calendar.objects.get(date_time=next_visit)
                    next_calendar_record.is_free = True
                    next_calendar_record.save()

                except Calendar.DoesNotExist:
                    pass

            item.calendar.is_free = True
            item.calendar.save()

        queryset.delete()

    def delete_model(self, request, obj):

        obj.delete()
