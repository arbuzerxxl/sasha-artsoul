from django.contrib.auth import get_user_model
from rest_framework.serializers import (ModelSerializer, HyperlinkedIdentityField, PrimaryKeyRelatedField, ValidationError, Field)
from services.models import Visit, Client, Master, Calendar


class ChoicesField(Field):

    def __init__(self, choices, **kwargs):
        self._choices = choices
        super(ChoicesField, self).__init__(**kwargs)

    def to_representation(self, obj):

        for choice in self._choices.choices:
            if choice[0] == obj:
                return choice[1]
        return None

    def to_internal_value(self, data):

        for choice in self._choices.choices:
            if choice[1] == data:
                return choice[0]
        return None


class UserSerializer(ModelSerializer):

    detail_url = HyperlinkedIdentityField(view_name='users-detail')

    class Meta:
        model = get_user_model()
        queryset = model.objects.all()
        fields = ('id', 'phone_number', 'telegram_id', 'email', 'password',
                  'last_name', 'first_name', 'is_superuser', 'is_staff', 'detail_url')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        password = validated_data.pop('password', '')
        user = self.Meta.model(**validated_data)
        user.set_password(password)
        user.save()
        return user

    def update(self, instance, validated_data):
        instance.set_password(validated_data.pop('password', ''))
        return super().update(instance, validated_data)


class VisitSerializer(ModelSerializer):

    pretty_calendar = PrimaryKeyRelatedField(read_only=True, source='calendar.__str__')
    discount = ChoicesField(choices=Visit.Discounts)

    class Meta:
        model = Visit
        fields = ('client', 'calendar', 'pretty_calendar', 'service', 'status', 'service_price', 'discount', 'extra', 'extra_total', 'total', 'rating', )

    def validate_client(self, value):

        try:
            calendar = Calendar.objects.get(pk=self.instance.calendar_id)
            month = calendar.date_time.month
            any_visits = Visit.objects.filter(client=self.initial_data['client'], calendar__date_time__month=month)
            client = Client.objects.get(user=self.initial_data['client'])

            if any_visits and any_visits.count() >= 2 and client.user_type == 'Первый визит':
                raise ValidationError(detail='На данный момент Вы не можете иметь больше 2 записей')

        except (Calendar.DoesNotExist, Client.DoesNotExist):
            pass

        return value

    def validate_service(self, value):

        next_calendar: Calendar | None = Visit.searchNextCalendarEntry(visit=self, service=value)

        if next_calendar and next_calendar.is_free is False:
            raise ValidationError(detail="'Наращивание' и 'Коррекция' требуют больше 2 часов работы. Найдите более подходящее время записи.")

        return value


class ThinVisitSerializer(ModelSerializer):

    detail_url = HyperlinkedIdentityField(view_name='visits-detail')
    pretty_calendar = PrimaryKeyRelatedField(read_only=True, source='calendar.__str__')
    pretty_client = PrimaryKeyRelatedField(read_only=True, source='client.user.__str__')

    class Meta:
        model = Visit
        fields = ('client', 'calendar', 'pretty_calendar', 'pretty_client', 'service', 'detail_url', )


class ClientsSerializer(ModelSerializer):

    detail_url = HyperlinkedIdentityField(view_name='clients-detail')
    pretty_client = PrimaryKeyRelatedField(read_only=True, source='user.__str__')

    class Meta:
        model = Client
        fields = ('user', 'pretty_client', 'user_type', 'detail_url')


class MastersSerializer(ModelSerializer):

    detail_url = HyperlinkedIdentityField(view_name='masters-detail')
    pretty_master = PrimaryKeyRelatedField(read_only=True, source='user.__str__')

    class Meta:
        model = Master
        fields = ('user', 'pretty_master', 'user_type', 'detail_url')


class CalendarSerializer(ModelSerializer):

    detail_url = HyperlinkedIdentityField(view_name='calendar-detail')
    master_full_name = PrimaryKeyRelatedField(read_only=True, source='master.user.__str__')

    class Meta:
        model = Calendar
        fields = ('id', 'master', 'master_full_name', 'date_time', 'is_free', 'detail_url')
