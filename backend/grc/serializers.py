from rest_framework import serializers
from .models import Audit, Framework, Policy, Users, SubPolicy, Compliance
from django.contrib.auth.models import User
from datetime import date

# Serializer for Audit
class AuditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Audit
        fields = ['AuditId', 'Assignee', 'Auditor', 'Reviewer', 'FrameworkId', 'PolicyId', 'DueDate', 'Frequency', 'AuditType', 'Status']

# Serializer for Framework
class FrameworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Framework
        fields = ['FrameworkId', 'FrameworkName', 'FrameworkDescription']

# Serializer for Policy
class PolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = Policy
        fields = ['PolicyId', 'PolicyName', 'PolicyDescription', 'FrameworkId']

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = Users
        fields = ['UserId', 'UserName', 'Email', 'Role']

class PolicyAllocationSerializer(serializers.Serializer):
    framework = serializers.IntegerField(required=True)
    policy = serializers.IntegerField(required=False, allow_null=True)
    subpolicy = serializers.IntegerField(required=False, allow_null=True)
    auditor = serializers.IntegerField(required=True)
    assignee = serializers.IntegerField(required=True)
    reviewer = serializers.IntegerField(required=False, allow_null=True)
    duedate = serializers.DateField(required=True)
    frequency = serializers.IntegerField(required=True)
    audit_type = serializers.CharField(required=True, max_length=1)
    selected_reports = serializers.ListField(child=serializers.IntegerField(), required=False, default=list)
    
    def validate_policy(self, value):
        # Convert empty string to null
        if value == '':
            return None
        return value
    
    def validate_subpolicy(self, value):
        # Convert empty string to null
        if value == '':
            return None
        return value
    
    def validate_reviewer(self, value):
        # Convert empty string to null
        if value == '':
            return None
        return value

    # Custom validation for due date
    def validate_duedate(self, value):
        if value < date.today():
            raise serializers.ValidationError("Due date cannot be in the past.")
        return value
    
    def validate_audit_type(self, value):
        # Convert 'Internal' to 'I' and 'External' to 'E'
        if value == 'Internal':
            return 'I'
        elif value == 'External':
            return 'E'
        # If already the single character, just return it
        elif value in ['I', 'E']:
            return value
        else:
            raise serializers.ValidationError("Invalid audit type. Must be 'Internal' or 'External'.")

# Compliance Item serializer
class ComplianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compliance
        fields = [
            'ComplianceId', 
            'SubPolicyId', 
            'ComplianceItemDescription', 
            'IsRisk', 
            'Criticality', 
            'MandatoryOptional'
        ]