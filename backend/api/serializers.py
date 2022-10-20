
from datetime import datetime
from rest_framework.serializers import (ModelSerializer, DateTimeField, DecimalField, FloatField,
                                        SerializerMethodField, HyperlinkedIdentityField, StringRelatedField,
                                        IntegerField, CharField, ChoiceField, SlugRelatedField, EmailField)
from services.models import Visit, Client
from accounts.models import User
from django.contrib.auth import get_user_model
from django.utils.formats import number_format
import decimal


class UserSerializer(ModelSerializer):

    class Meta:
        model = get_user_model()
        queryset = model.objects.all()
        fields = ('id', 'phone_number', 'email', 'password', 'last_name', 'first_name', 'is_client', 'is_superuser')
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

    # visit_date = DateTimeField(label='Дата и время записи', help_text='Необходимо указать. Укажите дату и время записи', format='%d-%m-%Y %H:%M')

    class Meta:
        model = Visit
        fields = '__all__'

    def create(self, validated_data):

        request_visit_date = validated_data.pop('visit_date')
        obj_visit_date = datetime.strptime(request_visit_date, "%Y-%m-%dT%H:%M")
        visit_date = obj_visit_date.strftime('%d-%m-%Y %H:%M')
        validated_data['visit_date'] = visit_date
        visit = self.Meta.model(**validated_data)
        visit.save()
        return visit


class ThinVisitSerializer(ModelSerializer):
    detail_url = HyperlinkedIdentityField(view_name='visits-detail')

    class Meta:
        model = Visit
        fields = ('visit_date', 'client', 'master', 'service', 'detail_url',)


class ClientsSerializer(ModelSerializer):
    detail_url = HyperlinkedIdentityField(view_name='clients-detail', )

    class Meta:
        model = Client
        fields = ('user', 'client_type', 'detail_url')
