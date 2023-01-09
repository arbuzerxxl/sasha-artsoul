import calendar
from datetime import datetime
from django.contrib.auth import get_user_model
from django.db.models import Sum, DecimalField, Q
from services.models import Visit, Client, Master, Calendar
from api.serializers import (VisitSerializer, UserSerializer, ThinVisitSerializer,
                             ClientsSerializer, MastersSerializer, CalendarSerializer,)

from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAdminUser
from rest_framework.response import Response
from .permissions import IsClient


class UserViewSet(ModelViewSet):

    model = get_user_model()
    queryset = model.objects.none()
    serializer_class = UserSerializer
    permission_classes = (IsAdminUser, )

    def get_queryset(self):
        if self.request.data.get('_phone_number', None):
            return self.model.objects.filter(phone_number=self.request.data['_phone_number'])
        elif self.request.data.get('_is_staff', None):
            return self.model.objects.filter(is_staff=self.request.data['_is_staff'])
        elif self.request.data.get('_telegram_id', None):
            return self.model.objects.filter(telegram_id=self.request.data['_telegram_id'])
        else:
            return self.model.objects.all()


class VisitViewSet(ModelViewSet):

    model = Visit
    queryset = model.objects.all()
    serializer_class = VisitSerializer
    permission_classes = (IsClient, )

    def get_serializer_class(self):
        if self.action == 'list':
            return ThinVisitSerializer
        return VisitSerializer

    def get_queryset(self):

        if self.request.user.is_superuser:
            # зарег. клиент: просмотр своих пред. записей
            if self.request.data.get('_client_tg_id') and self.request.data.get('_status'):
                return self.model.objects.filter(client__user__telegram_id=self.request.data.get('_client_tg_id'),
                                                 status=self.request.data.get('_status'))
            # зарег. клиент: просмотр истории всех записей, включая предварительные
            elif self.request.data.get('_client_tg_id'):
                return self.model.objects.filter(client__user__telegram_id=self.request.data.get('_client_tg_id'))
            # зарег. мастер: просмотр своих активных записей
            elif self.request.data.get('_master_tg_id') and self.request.data.get('_status'):
                return self.model.objects.filter(calendar__master__user__telegram_id=self.request.data.get('_master_tg_id'),
                                                 status=self.request.data.get('_status'))
            # зарег. мастер: просмотр истории записей за определенный месяц
            elif self.request.data.get('_master_tg_id') and self.request.data.get('_month'):
                return self.model.objects.filter(calendar__master__user__telegram_id=self.request.data.get('_master_tg_id'),
                                                 calendar__date_time__month=self.request.data.get('_month'))
            # зарег. мастер: просмотр истории всех записей, включая предварительные
            elif self.request.data.get('_master_tg_id'):
                return self.model.objects.filter(calendar__master__user__telegram_id=self.request.data.get('_master_tg_id'))
            # админ: просмотр записей за определенный день
            elif self.request.data.get('_day') and self.request.data.get('_month') and self.request.data.get('_year'):
                return self.model.objects.filter(calendar__date_time__day=self.request.data.get('_day'),
                                                 calendar__date_time__month=self.request.data.get('_month'),
                                                 calendar__date_time__year=self.request.data.get('_year'))
            # админ: поиск записей клиента за определенный месяц у определенного мастера
            elif self.request.data.get('_client') and self.request.data.get('_month') and self.request.data.get('_master'):
                return self.model.objects.filter(calendar__date_time__month=self.request.data.get('_month'),
                                                 calendar__master=self.request.data.get('_master'),
                                                 client=self.request.data.get('_client'))
            # админ: просмотр записей клиента за определенный месяц
            elif self.request.data.get('_client') and self.request.data.get('_month'):
                return self.model.objects.filter(calendar__date_time__month=self.request.data.get('_month'),
                                                 client=self.request.data.get('_client'))
            # админ: просмотр записей по статусам
            elif self.request.data.get('_status'):
                return self.model.objects.filter(status=self.request.data.get('_status'))
            # отображение всех записей в БД
            else:
                return self.model.objects.all()
        if not self.request.user.is_anonymous:
            return self.model.objects.filter(client__user=self.request.user)


class VisitCountSerializer(APIView):

    def get(self, request, format=None):

        current_year = self.request.data.get('_year')
        current_month = self.request.data.get('_month')
        days_stat = {}

        if current_month and current_year:
            month = Visit.objects.filter(calendar__date_time__month=current_month,
                                         calendar__date_time__year=current_year)

            for day in range(1, calendar.monthrange(current_year, current_month)[1] + 1):
                days_stat[f'{day} {calendar.month_name[current_month]}'] = month.filter(calendar__date_time__day=day).count()

            return Response(days_stat)
        else:
            return Response("Данные не найдены")


class MonthProfitSerializer(APIView):

    def get(self, request, format=None):

        current_year = self.request.data.get('_year')
        current_month = self.request.data.get('_month')

        profit_month = Visit.objects.aggregate(sum=Sum('total', output_field=DecimalField(),
                                               filter=Q(calendar__date_time__month=current_month,
                                                        calendar__date_time__year=current_year)))
        return Response(data=(profit_month))


class YearProfitSerializer(APIView):

    def get(self, request, format=None):

        current_year = self.request.data.get('_year')

        profit_year = Visit.objects.aggregate(sum=Sum('total', output_field=DecimalField(),
                                              filter=Q(calendar__date_time__year=current_year)))
        return Response(data=(profit_year))


class ClientViewSet(ModelViewSet):

    model = Client
    queryset = model.objects.none()
    serializer_class = ClientsSerializer
    permission_classes = (IsAdminUser, )

    def get_queryset(self):

        if self.request.user.is_superuser and self.request.data.get('_three_week'):

            today_week = datetime.now().isocalendar()[1]

            if self.request.data.get('_three_week') == "manicure":
                clients = self.model.objects.filter(last_visit_manicure__week__lt=today_week)

                for client in clients:
                    if today_week - client.last_visit_manicure.isocalendar()[1] > 3:
                        continue
                    else:
                        clients = clients.exclude(pk=client.pk)

            elif self.request.data.get('_three_week') == "pedicure":
                clients = self.model.objects.filter(last_visit_pedicure__week__lt=today_week)

                for client in clients:
                    if today_week - client.last_visit_pedicure.isocalendar()[1] > 3:
                        continue
                    else:
                        clients = clients.exclude(pk=client.pk)

            elif self.request.data.get('_three_week') == "free_manicure":
                clients = self.model.objects.filter(last_visit_manicure=None)

            elif self.request.data.get('_three_week') == "free_pedicure":
                clients = self.model.objects.filter(last_visit_pedicure=None)

            else:
                clients = None

            return clients

        elif self.request.data.get('_user', None):
            return self.model.objects.filter(user=self.request.data['_user'])
        else:
            return self.model.objects.all()


class MasterViewSet(ModelViewSet):

    model = Master
    queryset = model.objects.none()
    serializer_class = MastersSerializer
    permission_classes = (IsAdminUser, )

    def get_queryset(self):
        if self.request.data.get('_user', None):
            return self.model.objects.filter(user=self.request.data['_user'])
        else:
            return self.model.objects.all()


class CalendarViewSet(ModelViewSet):

    model = Calendar
    queryset = model.objects.none()
    serializer_class = CalendarSerializer
    permission_classes = (IsAdminUser, )

    def get_queryset(self):
        if self.request.data.get('_month', None) and self.request.data.get('_master', None) and self.request.data.get('_is_free', None):
            return self.model.objects.filter(date_time__month=self.request.data['_month'],
                                             master=self.request.data['_master'],
                                             is_free=self.request.data['_is_free']
                                             )

        if self.request.data.get('_date_time', None) and self.request.data.get('_master', None):
            return self.model.objects.filter(date_time=self.request.data['_date_time'], master=self.request.data['_master'])
        elif self.request.data.get('_is_free', None):
            return self.model.objects.filter(is_free=self.request.data['_is_free'])
        else:
            return self.model.objects.all()
