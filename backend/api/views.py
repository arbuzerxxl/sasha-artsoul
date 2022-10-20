from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from services.models import Visit, Client
from api.serializers import VisitSerializer, UserSerializer, ThinVisitSerializer, ClientsSerializer
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from .permissions import IsClient


class UserViewSet(ModelViewSet):
    model = get_user_model()
    queryset = model.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser, )


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
        if self.request.user.is_superuser:
            return self.model.objects.all()
