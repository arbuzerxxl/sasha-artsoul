from django.shortcuts import render
from django.http import HttpResponse
from .models import Visit


from django_nextjs.render import render_nextjs_page_sync


def index(request):
    return render_nextjs_page_sync(request)

# def index(request):
#     visits = Visit.objects.all()

#     return render(request, 'index.html',
#                   context={'visits': visits})

