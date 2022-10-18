
from rest_framework.serializers import (ModelSerializer, DateTimeField, DecimalField, FloatField,
                                        SerializerMethodField, HyperlinkedIdentityField, StringRelatedField, IntegerField, CharField, ChoiceField)
from services.models import Visit
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

    # visit_date = DateTimeField(label='Дата и время записи', help_text='Необходимо указать. Укажите дату и время записи',)
    # client = CharField(source='client.__str__')
    # master = StringRelatedField()
    # rating = CharField(source='get_rating_display', label='Ваша оценка', help_text='Здесь Вы можете указать вашу оценку')

    class Meta:
        model = Visit
        fields = '__all__'
        # extra_kwargs = {'client': {'source': 'get_client_name'},
        #                 'rating': {'source': 'get_rating_display'}}


class ThinVisitSerializer(ModelSerializer):
    detail_url = HyperlinkedIdentityField(view_name='visits-detail')
    client = StringRelatedField()
    master = StringRelatedField()

    class Meta:
        model = Visit
        fields = ('visit_date', 'client', 'master', 'service_price', 'detail_url',)
