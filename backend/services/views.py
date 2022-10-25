from django.shortcuts import render
from django.http import HttpResponse
from django.contrib.auth import authenticate, login
from .models import Visit, Client
# from accounts.models import User
from django.views.decorators.csrf import csrf_exempt

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
