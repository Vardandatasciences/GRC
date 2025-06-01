from rest_framework import serializers
from .models import Framework, Policy, SubPolicy, PolicyApproval, Incident, RiskInstance, Compliance
from datetime import date
from django.contrib.auth.models import User

class SubPolicySerializer(serializers.ModelSerializer):
    CreatedByName = serializers.CharField(required=False, allow_blank=True)
    Status = serializers.CharField(required=False, default='Under Review')
    PermanentTemporary = serializers.CharField(required=False, default='Permanent')

    class Meta:
        model = SubPolicy
        fields = [
            'SubPolicyId', 'SubPolicyName', 'CreatedByName', 'CreatedByDate',
            'Identifier', 'Description', 'Status', 'PermanentTemporary',
            'Control', 'PolicyId'
        ]

class PolicySerializer(serializers.ModelSerializer):
    FrameworkCategory = serializers.CharField(source='FrameworkId.Category', read_only=True)
    FrameworkName = serializers.CharField(source='FrameworkId.FrameworkName', read_only=True)
    subpolicies = serializers.SerializerMethodField()
    CreatedByName = serializers.CharField(required=False, allow_blank=True)
    Reviewer = serializers.CharField(required=False, allow_blank=True)
    Status = serializers.CharField(required=False, default='Under Review')
    ActiveInactive = serializers.CharField(required=False, default='Inactive')
    CoverageRate = serializers.FloatField(required=False, allow_null=True)

    def get_subpolicies(self, obj):
        # Get all subpolicies without filtering by status
        subpolicies = obj.subpolicy_set.all()
        return SubPolicySerializer(subpolicies, many=True).data

    class Meta:
        model = Policy
        fields = [
            'PolicyId', 'CurrentVersion', 'Status', 'PolicyName', 'PolicyDescription',
            'StartDate', 'EndDate', 'Department', 'CreatedByName', 'CreatedByDate',
            'Applicability', 'DocURL', 'Scope', 'Objective', 'Identifier',
            'PermanentTemporary', 'ActiveInactive', 'FrameworkId', 'Reviewer',
            'FrameworkCategory', 'FrameworkName', 'subpolicies', 'CoverageRate'
        ]

class FrameworkSerializer(serializers.ModelSerializer):
    policies = serializers.SerializerMethodField()
    CreatedByName = serializers.CharField(required=False, allow_blank=True)
    Reviewer = serializers.CharField(required=False, allow_blank=True)
    
    def get_policies(self, obj):
        # Filter policies to only include Approved and Active ones
        policies = obj.policy_set.filter(Status='Approved', ActiveInactive='Active')
        return PolicySerializer(policies, many=True).data
    
    class Meta:
        model = Framework
        fields = [
            'FrameworkId', 'FrameworkName', 'CurrentVersion', 'FrameworkDescription',
            'EffectiveDate', 'CreatedByName', 'CreatedByDate', 'Category',
            'DocURL', 'Identifier', 'StartDate', 'EndDate', 'Status',
            'ActiveInactive', 'policies', 'Reviewer'
        ]

class ComplianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compliance
        fields = '__all__'  # Include all fields in the model

class PolicyAllocationSerializer(serializers.Serializer):
    framework = serializers.IntegerField(required=True, error_messages={'required': 'Framework is required', 'invalid': 'Framework must be a valid integer'})
    policy = serializers.IntegerField(required=False, allow_null=True)
    subpolicy = serializers.IntegerField(required=False, allow_null=True)
    assignee = serializers.IntegerField(required=True, error_messages={'required': 'Assignee is required', 'invalid': 'Assignee must be a valid user ID'})
    auditor = serializers.IntegerField(required=True, error_messages={'required': 'Auditor is required', 'invalid': 'Auditor must be a valid user ID'})
    reviewer = serializers.IntegerField(required=False, allow_null=True)
    duedate = serializers.DateField(required=True, error_messages={'required': 'Due date is required', 'invalid': 'Due date must be in YYYY-MM-DD format'})
    frequency = serializers.IntegerField(required=True, error_messages={'required': 'Frequency is required', 'invalid': 'Frequency must be a valid integer'})
    audit_type = serializers.CharField(max_length=1, required=True, error_messages={'required': 'Audit type is required', 'invalid': 'Audit type must be either Internal (I) or External (E)'})
   
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
        

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'first_name', 'last_name']
        extra_kwargs = {'password': {'write_only': True}}
 
    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

class PolicyApprovalSerializer(serializers.ModelSerializer):
    ApprovedDate = serializers.DateField(read_only=True)
    PolicyId = serializers.PrimaryKeyRelatedField(source='PolicyId.PolicyId', read_only=True)
    
    class Meta:
        model = PolicyApproval
        fields = [
            'ApprovalId', 'ExtractedData', 'UserId', 
            'ReviewerId', 'Version', 'ApprovedNot', 'ApprovedDate', 'PolicyId'
        ]

class IncidentSerializer(serializers.ModelSerializer):
    has_risk_instance = serializers.SerializerMethodField()

    class Meta:
        model = Incident
        fields = '__all__'  # or list all fields explicitly + 'has_risk_instance'

    def get_has_risk_instance(self, obj):
        return RiskInstance.objects.filter(IncidentId=obj.IncidentId).exists()