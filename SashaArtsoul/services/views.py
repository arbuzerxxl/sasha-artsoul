from django.shortcuts import render
from django.http import HttpResponse
from .models import Visit


def index(request):
    visits = Visit.objects.all()

    return render(request, 'index.html',
                  context={'visits': visits})

