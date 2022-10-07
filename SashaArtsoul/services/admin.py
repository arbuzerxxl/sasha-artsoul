from django.contrib import admin
from .models import Service, Client, Master, Visit, Discount

# Register your models here.
admin.site.register(Service)
admin.site.register(Client)
admin.site.register(Master)


@admin.register(Discount)
class DiscountAdmin(admin.ModelAdmin):
    list_display = ('name', 'value')


@admin.register(Visit)
class VisitAdmin(admin.ModelAdmin):
    list_display = ('visit_date', 'status', 'service', 'client', 'master', 'total', 'review', 'rating')
    list_filter = ('visit_date', 'status', 'client')
