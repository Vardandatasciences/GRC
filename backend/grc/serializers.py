from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Risk
from .models import Incident
from .models import Compliance
from .models import RiskInstance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user 
    

class RiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Risk
        fields = '__all__'  # Include all fields in the model


class IncidentSerializer(serializers.ModelSerializer):
    has_risk_instance = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = '__all__'  # or list all fields explicitly + 'has_risk_instance'

    def get_has_risk_instance(self, obj):
        return RiskInstance.objects.filter(IncidentId=obj.IncidentId).exists()


class ComplianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compliance
        fields = '__all__'  # Include all fields in the model


class RiskInstanceSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskInstance
        fields = '__all__'