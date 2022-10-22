
from api.views import *
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('visits', VisitViewSet, basename='visits')
router.register('users', UserViewSet, basename='users')
router.register('clients', ClientViewSet, basename='clients')
urlpatterns = router.urls
