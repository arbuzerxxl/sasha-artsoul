
from django.urls import path
from rest_framework.urlpatterns import format_suffix_patterns
from api.views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('visits', VisitViewSet, basename='visits')
router.register('users', UserViewSet, basename='users')
urlpatterns = router.urls

# notes_list = NoteViewSet.as_view({
#     'get': 'list',
#     'post': 'create'}
# )
# notes_detail = NoteViewSet.as_view({
#     'get': 'retrieve',
#     'put': 'update',
#     'patch': 'partial_update',
#     'delete': 'destroy'
# })

# urlpatterns = [
#     path('visits/', visits_list, name='visits-list'),
#     path('visits/<int:pk>/', visits_detail, name='visits-detail'),
# ]
# urlpatterns = format_suffix_patterns(urlpatterns)
