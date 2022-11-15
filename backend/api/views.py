from django.contrib.auth import get_user_model
from services.models import Visit, Client, Master, Calendar
from api.serializers import (VisitSerializer, UserSerializer, ThinVisitSerializer,
                             ClientsSerializer, MastersSerializer, CalendarSerializer)
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from .permissions import IsClient


class UserViewSet(ModelViewSet):
    model = get_user_model()
    queryset = model.objects.none()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser, )

    def get_queryset(self):
        if self.request.data.get('phone_number', None):
            return self.model.objects.filter(phone_number=self.request.data['phone_number'])
        elif self.request.data.get('is_client', None):
            return self.model.objects.filter(is_client=self.request.data['is_client'])
        else:
            return self.model.objects.all()


class VisitViewSet(ModelViewSet):
    model = Visit
    queryset = model.objects.none()
    serializer_class = VisitSerializer
    permission_classes = (IsClient, )

    def get_serializer_class(self):
        if self.action == 'list':
            return ThinVisitSerializer
        return VisitSerializer

    def get_queryset(self):
        if self.request.user.is_superuser:
            return self.model.objects.all()
        if not self.request.user.is_anonymous:
            return self.model.objects.filter(client__user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(client__user=self.request.user)


class ClientViewSet(ModelViewSet):
    model = Client
    queryset = model.objects.none()
    serializer_class = ClientsSerializer
    permission_classes = (IsAdminUser, )

    def get_queryset(self):
        if self.request.data.get('user', None):
            return self.model.objects.filter(user=self.request.data['user'])
        else:
            return self.model.objects.all()  # TODO: возможно придется поменять для админа


class MasterViewSet(ModelViewSet):
    model = Master
    queryset = model.objects.none()
    serializer_class = MastersSerializer
    permission_classes = (IsAdminUser, )

    def get_queryset(self):
        if self.request.data.get('user', None):
            return self.model.objects.filter(user=self.request.data['user'])
        else:
            return self.model.objects.all()


class CalendarViewSet(ModelViewSet):
    model = Calendar
    queryset = model.objects.none()
    serializer_class = CalendarSerializer
    permission_classes = (IsAdminUser, )

    def get_queryset(self):
        if self.request.data.get('date_time', None):
            return self.model.objects.filter(date_time=self.request.data['date_time'])
        else:
            return self.model.objects.all()
