from rest_framework import serializers
from university.models import Statement


class StatementSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statement
        fields = '__all__'


class ChangeStatementStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model = Statement
        fields = ('id', 'status')

