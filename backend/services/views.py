from django.shortcuts import render
from django.http import HttpResponse
from .models import Visit, Client
from accounts.models import User

# from django_nextjs.render import render_nextjs_page_sync


# def index_js(request):
#     return render_nextjs_page_sync(request)


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
