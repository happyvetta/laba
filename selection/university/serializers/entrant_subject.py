from rest_framework import serializers
from account.models import EntrantSubject


class EntrantSubjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = EntrantSubject
        fields = '__all__'
