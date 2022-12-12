from datetime import datetime
import calendar
from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .models import Visit, Master, Calendar
from accounts.models import User
from django.views.decorators.csrf import csrf_exempt
from django.db import IntegrityError
from django_nextjs.render import render_nextjs_page_sync


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

    visits = None

    if request.user.is_authenticated:
        visits = Visit.objects.filter(client=request.user.phone_number)

    return render(request, 'index.html',
                  context={'visits': visits})


#  add cookie example
def home(request):

    response = HttpResponse('XWHAT?!')
    # response = render(request, template='index.html')  # django.http.HttpResponse
    response.set_cookie(key='id', value=1)
    return response


def create_calendar(request):
    try:
        User.objects.create_superuser('89999999999',
                                      '',
                                      '1234',
                                      last_name='ADMIN',
                                      first_name='ADMIN')
    except IntegrityError:
        pass
    try:
        Master.objects.create(user=User.objects.get(pk=1), user_type='Топ-мастер')
    except IntegrityError:
        pass

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

    return HttpResponse("Суперпользователь создан")
