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
        if self.request.data.get('phone_number', None):
            return self.model.objects.filter(phone_number=self.request.data['phone_number'])
        elif self.request.data.get('is_client', None):
            return self.model.objects.filter(is_client=self.request.data['is_client'])
        elif self.request.data.get('telegram_id', None):
            return self.model.objects.filter(telegram_id=self.request.data['telegram_id'])
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
            if self.request.data.get('client_tg_id') and self.request.data.get('status'):
                return self.model.objects.filter(client__user__telegram_id=self.request.data.get('client_tg_id'),
                                                 status=self.request.data.get('status'))
            # зарег. клиент: просмотр истории всех записей, включая предварительные
            elif self.request.data.get('client_tg_id'):
                return self.model.objects.filter(client__user__telegram_id=self.request.data.get('client_tg_id'))
            # зарег. мастер: просмотр своих активных записей
            elif self.request.data.get('master_tg_id') and self.request.data.get('status'):
                return self.model.objects.filter(calendar__master__user__telegram_id=self.request.data.get('master_tg_id'),
                                                 status=self.request.data.get('status'))
            # зарег. мастер: просмотр истории записей за определенный месяц
            elif self.request.data.get('master_tg_id') and self.request.data.get('month'):
                return self.model.objects.filter(calendar__master__user__telegram_id=self.request.data.get('master_tg_id'),
                                                 calendar__date_time__month=self.request.data.get('month'))
            # зарег. мастер: просмотр истории всех записей, включая предварительные
            elif self.request.data.get('master_tg_id'):
                return self.model.objects.filter(calendar__master__user__telegram_id=self.request.data.get('master_tg_id'))
            # админ: просмотр записей за определенный день
            elif self.request.data.get('day') and self.request.data.get('month') and self.request.data.get('year'):
                return self.model.objects.filter(calendar__date_time__day=self.request.data.get('day'),
                                                 calendar__date_time__month=self.request.data.get('month'),
                                                 calendar__date_time__year=self.request.data.get('year'))
            # админ: просмотр записей по статусам
            elif self.request.data.get('status'):
                return self.model.objects.filter(status=self.request.data.get('status'))
            # админ: просмотр нагруженности по дням за определенный месяц

            # отображение всех записей в БД
            else:
                return self.model.objects.all()
        if not self.request.user.is_anonymous:
            return self.model.objects.filter(client__user=self.request.user)


class VisitCountSerializer(APIView):

    def get(self, request, format=None):

        current_year = self.request.data.get('year')
        current_month = self.request.data.get('month')
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

        current_year = self.request.data.get('year')
        current_month = self.request.data.get('month')

        profit_month = Visit.objects.aggregate(sum=Sum('total', output_field=DecimalField(),
                                               filter=Q(calendar__date_time__month=current_month,
                                                        calendar__date_time__year=current_year)))
        return Response(data=(profit_month))


class YearProfitSerializer(APIView):

    def get(self, request, format=None):

        current_year = self.request.data.get('year')

        profit_year = Visit.objects.aggregate(sum=Sum('total', output_field=DecimalField(),
                                              filter=Q(calendar__date_time__year=current_year)))
        return Response(data=(profit_year))


class ClientViewSet(ModelViewSet):

    model = Client
    queryset = model.objects.none()
    serializer_class = ClientsSerializer
    permission_classes = (IsAdminUser, )

    def get_queryset(self):

        if self.request.user.is_superuser and self.request.data.get('three_week'):

            today_week = datetime.now().isocalendar()[1]

            if self.request.data.get('three_week') == "manicure":
                clients = self.model.objects.filter(last_visit_manicure__week__lt=today_week)

                for client in clients:
                    if today_week - client.last_visit_manicure.isocalendar()[1] > 3:
                        continue
                    else:
                        clients = clients.exclude(pk=client.pk)

            elif self.request.data.get('three_week') == "pedicure":
                clients = self.model.objects.filter(last_visit_pedicure__week__lt=today_week)

                for client in clients:
                    if today_week - client.last_visit_pedicure.isocalendar()[1] > 3:
                        continue
                    else:
                        clients = clients.exclude(pk=client.pk)

            elif self.request.data.get('three_week') == "free_manicure":
                clients = self.model.objects.filter(last_visit_manicure=None)

            elif self.request.data.get('three_week') == "free_pedicure":
                clients = self.model.objects.filter(last_visit_pedicure=None)

            else:
                clients = None

            return clients

        elif self.request.data.get('user', None):
            return self.model.objects.filter(user=self.request.data['user'])
        else:
            return self.model.objects.all()


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
        if self.request.data.get('month', None) and self.request.data.get('master', None) and self.request.data.get('is_free', None):
            return self.model.objects.filter(date_time__month=self.request.data['month'],
                                             master=self.request.data['master'],
                                             is_free=self.request.data['is_free']
                                             )

        if self.request.data.get('date_time', None) and self.request.data.get('master', None):
            return self.model.objects.filter(date_time=self.request.data['date_time'], master=self.request.data['master'])
        elif self.request.data.get('is_free', None):
            return self.model.objects.filter(is_free=self.request.data['is_free'])
        else:
            return self.model.objects.all()
