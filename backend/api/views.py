from django.shortcuts import render
from django.contrib.auth import get_user_model
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from services.models import Visit
from api.serializers import VisitSerializer, UserSerializer, ThinVisitSerializer
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

    # def perform_create(self, serializer):
    #     serializer.save(client__user=self.request.user)


# @api_view(['GET', 'POST'])
# def visits_list(request, format=None):
#     if request.method == 'GET':
#         visits = Visit.objects.all()
#         serializer = VisitSerializer(visits, many=True)
#         return Response(serializer.data)
#     elif request.method == 'POST':
#         serializer = VisitSerializer(data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# @api_view(['GET', 'PUT', 'DELETE'])
# def visits_detail(request, pk, format=None):
#     try:
#         visit = Visit.objects.get(pk=pk)
#     except Visit.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#     if request.method == 'GET':
#         serializer = VisitSerializer(visit)
#         return Response(serializer.data)
#     elif request.method == 'PUT':
#         serializer = VisitSerializer(visit, data=request.data)
#         if serializer.is_valid():
#             serializer.save()
#             return Response(serializer.data, status=status.HTTP_201_CREATED)
#         return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
#     elif request.method == 'DELETE':
#         visit.delete()
#         return Response(status=status.HTTP_204_NO_CONTENT)
