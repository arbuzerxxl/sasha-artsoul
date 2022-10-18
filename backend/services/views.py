from django.shortcuts import render
from django.http import HttpResponse
from .models import Visit, Client
from accounts.models import User

from django_nextjs.render import render_nextjs_page_sync


def index(request):
    return render_nextjs_page_sync(request)


def index(request):
    user = User.objects.get(last_name='Kurbatova', first_name='Tatyana')
    client = Client.objects.get(user=user.id)
    
    visits = Visit.objects.filter(client=client.id)

    return render(request, 'index.html',
                  context={'visits': visits})
