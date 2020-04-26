from rest_framework import serializers
from university.models import Faculty


class FacultySerializer(serializers.ModelSerializer):
    class Meta:
        model = Faculty
        fields = '__all__'
