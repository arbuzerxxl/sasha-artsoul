from django.shortcuts import render
from django.http import HttpResponse
from .models import Visit, Client, Master, Discount, Service
from django.contrib.auth.models import User


def index(request):
    visits = Visit.objects.all()

    return render(request, 'index.html',
                  context={'visits': visits})


def insert_data(request):
    if Discount.objects.all():
        pass
    else:
        for name in Discount.DISCOUNTS_PRICE.keys():
            Discount.objects.create_discount(name=name)
    if Service.objects.all():
        pass
    else:
        for name in Service.SERVICES_PRICE.keys():
            Service.objects.create_service(name=name)

    return HttpResponse('Данные успешно добавлены')
