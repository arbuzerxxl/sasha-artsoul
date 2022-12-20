import ujson
import calendar
from datetime import datetime
from decimal import Decimal, getcontext
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .models import Visit, Master, Calendar, Client
from accounts.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django_nextjs.render import render_nextjs_page_sync

getcontext().prec = 10


def index(request):
    return render_nextjs_page_sync(request)


# @csrf_exempt
def my_view(request):
    username = request.POST['username']
    password = request.POST['password']
    user = authenticate(request, username=username, password=password)
    if user is not None:
        login(request, user)
        # return user
        return HttpResponse("Аутентификация прошла успешно")
    else:
        return HttpResponse("Неудачная аутентификация")


def index(request):

    return render(request, 'index.html')


#  add cookie example
def home(request):

    response = HttpResponse('XWHAT?!')
    # response = render(request, template='index.html')  # django.http.HttpResponse
    response.set_cookie(key='id', value=1)
    return response


def create_calendar(request):

    current_year = datetime.now().year
    current_month = datetime.now().month

    for day in range(1, calendar.monthrange(current_year, current_month)[1] + 1):
        try:
            if datetime(year=current_year, month=current_month, day=day).weekday() in [0, 1, 4, 5]:
                for hour in [10, 12, 15, 17]:
                    Calendar.objects.create(date_time=datetime(year=current_year,
                                                               month=current_month,
                                                               day=day,
                                                               hour=hour,
                                                               minute=0),
                                            master=Master.objects.get(pk=1))
        except IntegrityError:
            pass

    return redirect("index")


def add_old_clients(request):

    with open('../old_data/clients.json', 'r', encoding='utf-8') as jsonf:

        clients = ujson.load(jsonf)

        for client in clients:
            try:
                pw = "".join(list(client.get('phone_number'))[-1:-6:-1])
                user = User.objects.create(phone_number=client.get('phone_number'),
                                           last_name=client.get('last_name'),
                                           first_name=client.get('first_name'),
                                           telegram_id=None,
                                           is_client=True,
                                           email=None,
                                           password=pw)
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

            calendar = Calendar.objects.create(date_time=datetime.strptime(visit.get('Дата'), "%d-%m-%Y %H:%M"),
                                               master=Master.objects.get(pk=1))
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

            Visit.objects.create(calendar=calendar,
                                 status=visit.get('Тип записи'),
                                 service=visit.get('Тип услуги'),
                                 client=client,
                                 extra_total=extra_total,
                                 extra=visit.get('Дополнительные услуги'),
                                 discount=discount
                                 )

    return HttpResponse('Календарь создан')


def search_client(request):

    client = Client.objects.get(user_id__phone_number='')

    return HttpResponse(client)
