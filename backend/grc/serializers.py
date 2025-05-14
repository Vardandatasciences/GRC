from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Incident, AuditFindings, Users, Workflow, Compliance

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'username', 'email')
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = '__all__'
        extra_kwargs = {
            'audit_id': {'required': False, 'allow_null': True},
            'ComplianceId': {'required': False, 'allow_null': True},
            'UserId': {'required': False, 'allow_null': True},
            'mitigation': {'required': False, 'allow_null': True},
        } 

class AuditFindingsSerializer(serializers.ModelSerializer):
    is_risk = serializers.SerializerMethodField()

    class Meta:
        model = AuditFindings
        fields = '__all__'
        extra_fields = ['is_risk']

    def get_is_risk(self, obj):
        return obj.ComplianceId.IsRisk if obj.ComplianceId else False

class UsersSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['UserId', 'UserName'] 

class WorkflowSerializer(serializers.ModelSerializer):
    class Meta:
        model = Workflow
        fields = '__all__' 