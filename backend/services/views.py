import ujson
import calendar
from datetime import datetime
from decimal import Decimal, getcontext
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.utils import timezone
from django.db import IntegrityError
from django_nextjs.render import render_nextjs_page_sync
from .models import Visit, Master, Calendar, Client
from accounts.models import User

getcontext().prec = 10


def index(request):
    return render_nextjs_page_sync(request)


def index(request):

    return render(request, 'index.html')


def create_calendar(request):

    current_year = datetime.now().year
    current_month = datetime.now().month

    for day in range(1, calendar.monthrange(current_year, current_month)[1] + 1):
        try:
            if datetime(year=current_year, month=current_month, day=day).weekday() in [0, 1, 4, 5]:
                for hour in [10, 12, 15, 17]:

                    date_time = timezone.make_aware(datetime(year=current_year, month=current_month, day=day,
                                                             hour=hour, minute=0),)

                    Calendar.objects.create(date_time=date_time, master=Master.objects.get(pk=1))
        except IntegrityError:
            pass

    return redirect("index")


def add_old_clients(request):

    with open('../old_data/clients.json', 'r', encoding='utf-8') as jsonf:

        clients = ujson.load(jsonf)

        for client in clients:
            try:
                pw = "".join(list(client.get('phone_number'))[-1:-6:-1])
                user = User.objects.create(phone_number=client.get('phone_number'), last_name=client.get('last_name'),
                                           first_name=client.get('first_name'), telegram_id=None,
                                           email=None, password=pw)
                Client.objects.create(user=user)

            except IntegrityError:
                continue

    return HttpResponse('Клиенты созданы')


def add_old_calendar(request):

    DISCOUNTS = {
        'Первый визит': Decimal('0.15'),
        'Шестой визит': Decimal('0.35'),
        'Сарафан': Decimal('500')
    }

    with open('../old_data/visits.json', 'r') as jsonf:

        visits = ujson.load(jsonf)

        for visit in visits:

            date_time = timezone.make_aware(datetime.strptime(visit.get('Дата'), "%d-%m-%Y %H:%M"))

            calendar = Calendar.objects.create(date_time=date_time, master=Master.objects.get(pk=1))

            if not visit.get('Клиент'):
                client = None
            else:
                client = Client.objects.get(user_id__phone_number=visit.get('Клиент'))

            if visit.get('Скидка') in DISCOUNTS:
                discount = DISCOUNTS[visit.get('Скидка')]
            else:
                discount = None

            if not visit.get('Стоимость доп. услуги'):
                extra_total = None
            else:
                extra_total = Decimal(visit.get('Стоимость доп. услуги'))

            Visit.objects.create(calendar=calendar, status=visit.get('Тип записи'), service=visit.get('Тип услуги'),
                                 client=client, extra_total=extra_total, extra=visit.get('Дополнительные услуги'), discount=discount)

    return HttpResponse('Календарь создан')


def search_client(request):

    client = Client.objects.get(user_id__phone_number='')

    return HttpResponse(client)
