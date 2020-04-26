from rest_framework import serializers
from university.models import Special


class SpecialSerializer(serializers.ModelSerializer):
    class Meta:
        model = Special
        fields = '__all__'
