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

    class Meta:
        model = Visit
        fields = '__all__'


class ThinVisitSerializer(ModelSerializer):
    detail_url = HyperlinkedIdentityField(view_name='visits-detail')

    class Meta:
        model = Visit
        fields = ('calendar', 'client', 'service', 'detail_url',)


class ClientsSerializer(ModelSerializer):
    detail_url = HyperlinkedIdentityField(view_name='clients-detail')

    class Meta:
        model = Client
        fields = ('user', 'user_type', 'detail_url')


class MastersSerializer(ModelSerializer):
    detail_url = HyperlinkedIdentityField(view_name='masters-detail')

    class Meta:
        model = Master
        fields = ('user', 'user_type', 'detail_url')


class CalendarSerializer(ModelSerializer):
    detail_url = HyperlinkedIdentityField(view_name='calendar-detail')
    master_full_name = PrimaryKeyRelatedField(read_only=True, source='master.user.__str__')

    class Meta:
        model = Calendar
        fields = ('id', 'master', 'master_full_name', 'date_time', 'is_free', 'detail_url')
