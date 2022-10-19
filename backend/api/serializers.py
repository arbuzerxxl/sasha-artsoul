
from doctest import master
from rest_framework.serializers import (ModelSerializer, DateTimeField, DecimalField, FloatField,
                                        SerializerMethodField, HyperlinkedIdentityField, StringRelatedField,
                                        IntegerField, CharField, ChoiceField, SlugRelatedField, EmailField)
from services.models import Visit, Client
from accounts.models import User
from django.contrib.auth import get_user_model
from django.utils.formats import number_format
import decimal


class UserSerializer(ModelSerializer):  # TODO: Добавить сериализацию натуральных ключей в модели
    
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

    visit_date = DateTimeField(label='Дата и время записи', help_text='Необходимо указать. Укажите дату и время записи', format='%d-%m-%Y %H:%M')

    client = SlugRelatedField(slug_field='user_phone_number', queryset=Client.objects.all(),
                              label='Клиент', help_text='Необходимо указать. Укажите клиента',)

    class Meta:
        model = Visit
        fields = '__all__'


class ThinVisitSerializer(ModelSerializer):
    detail_url = HyperlinkedIdentityField(view_name='visits-detail')
    client = SlugRelatedField(slug_field='user_phone_number', queryset=Client.objects.all(),
                              label='Клиент', help_text='Необходимо указать. Укажите клиента',)

    class Meta:
        model = Visit
        fields = ('visit_date', 'client', 'master', 'service_price', 'detail_url',)


class ClientsSerializer(ModelSerializer):
    detail_url = HyperlinkedIdentityField(view_name='clients-detail', )
    user = SlugRelatedField(slug_field='phone_number', queryset=User.objects.all(),
                            label='Пользователь', help_text='Необходимо указать. Укажите пользователя',)

    class Meta:
        model = Client
        fields = ('user', 'client_type', 'detail_url')
