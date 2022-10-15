from rest_framework.serializers import (IntegerField, CharField, Serializer,
                                        ModelSerializer, HyperlinkedIdentityField, SerializerMethodField)
from services.models import Visit
from django.contrib.auth import get_user_model


class VisitSerializer(ModelSerializer):
    # author = SerializerMethodField(read_only=True)

    # def get_author(self, obj):
    #     return str(obj.author.email)

    class Meta:
        model = Visit
        fields = '__all__'
