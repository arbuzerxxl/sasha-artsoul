from rest_framework.serializers import (ModelSerializer, HyperlinkedIdentityField, PrimaryKeyRelatedField, CharField)
from services.models import Visit, Client, Master, Calendar
from django.contrib.auth import get_user_model


class UserSerializer(ModelSerializer):

    detail_url = HyperlinkedIdentityField(view_name='users-detail')

    class Meta:
        model = get_user_model()
        queryset = model.objects.all()
        fields = ('id', 'phone_number', 'telegram_id', 'email', 'password',
                  'last_name', 'first_name', 'is_client', 'is_superuser', 'detail_url')
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

    class Meta:
        model = Visit
        fields = ('client', 'calendar', 'pretty_calendar', 'service', 'service_price', 'extra', 'extra_total', 'total', 'rating', )


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
