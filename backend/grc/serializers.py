from rest_framework import serializers
from .models import Framework, Policy, SubPolicy, PolicyApproval, Incident, RiskInstance, Compliance
from datetime import date
from django.contrib.auth.models import User
from .models import Risk
from .models import Incident
from .models import Compliance
from .models import RiskInstance
from .models import RiskAssignment
from .models import GRCLog
import datetime

# Custom DateField to handle date objects properly
class SafeDateField(serializers.DateField):
    def to_representation(self, value):
        if isinstance(value, datetime.date):
            return value.isoformat()
        return super().to_representation(value)

# Custom DateTimeField to handle date objects properly
class SafeDateTimeField(serializers.DateTimeField):
    def to_representation(self, value):
        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            return value.isoformat()
        return super().to_representation(value)

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
    
class RiskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Risk
        fields = '__all__'  # Include all fields in the model

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


class ComplianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compliance
        fields = '__all__'  # Include all fields in the model


class RiskInstanceSerializer(serializers.ModelSerializer):
    # Add this custom field to handle any format of RiskMitigation
    RiskMitigation = serializers.JSONField(required=False, allow_null=True)
    MitigationDueDate = SafeDateField(required=False, allow_null=True)
    Date = SafeDateTimeField(required=False, allow_null=True)
    MitigationCompletedDate = SafeDateTimeField(required=False, allow_null=True)
    
    class Meta:
        model = RiskInstance
        fields = '__all__'
    
    def to_internal_value(self, data):
        # Convert the QueryDict or dict to a mutable dict
        mutable_data = data.copy() if hasattr(data, 'copy') else dict(data)
        
        # Set default values for required fields
        if not mutable_data.get('RiskOwner'):
            mutable_data['RiskOwner'] = 'System Owner'
        
        if not mutable_data.get('RiskStatus'):
            mutable_data['RiskStatus'] = 'Open'
        
        # Handle RiskMitigation if it's present but empty
        if 'RiskMitigation' in mutable_data and not mutable_data['RiskMitigation']:
            mutable_data['RiskMitigation'] = {}
        
        return super().to_internal_value(mutable_data)
    
    def to_representation(self, instance):
        # Create a custom representation instead of using the parent's method
        # This avoids the DateTimeField's enforce_timezone issues
        representation = {}
        
        # Process all fields manually to avoid DRF's datetime handling
        for field in self.fields.values():
            attribute = field.get_attribute(instance)
            
            # Skip if the attribute is None
            if attribute is None:
                representation[field.field_name] = None
                continue
                
            # Special handling for date/datetime fields
            if field.field_name in ['MitigationDueDate', 'Date', 'MitigationCompletedDate']:
                if hasattr(attribute, 'isoformat'):
                    representation[field.field_name] = attribute.isoformat()
                else:
                    representation[field.field_name] = attribute
            else:
                # For other fields, use the field's to_representation
                try:
                    representation[field.field_name] = field.to_representation(attribute)
                except Exception as e:
                    print(f"Error serializing {field.field_name}: {e}")
                    representation[field.field_name] = None
        
        return representation


class RiskAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RiskAssignment
        fields = ['id', 'risk', 'assigned_to', 'assigned_by', 'assigned_date']


class RiskWorkflowSerializer(serializers.ModelSerializer):
    assigned_to = serializers.SerializerMethodField()
    
    class Meta:
        model = Risk
        fields = ['id', 'title', 'description', 'severity', 'status', 'assigned_to']
        
    def get_assigned_to(self, obj):
        assignment = obj.assignments.first()
        if assignment:
            return assignment.assigned_to.username
        return None


class GRCLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = GRCLog
        fields = '__all__'
        
