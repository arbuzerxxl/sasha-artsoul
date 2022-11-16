
from api.views import *
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

router = DefaultRouter()
router.register('visits', VisitViewSet, basename='visits')
router.register('users', UserViewSet, basename='users')
router.register('clients', ClientViewSet, basename='clients')
router.register('masters', MasterViewSet, basename='masters')
router.register('calendar', CalendarViewSet, basename='calendar')
urlpatterns = router.urls

urlpatterns += [path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
                path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
                path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
                ]
