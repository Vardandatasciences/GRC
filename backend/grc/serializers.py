from rest_framework import serializers
from .models import Audit, Framework, Policy, Users, SubPolicy, Compliance, AuditFinding, Incident, Risk, RiskInstance, Workflow
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
        fields = ['FrameworkId', 'FrameworkName', 'CurrentVersion', 'Category']
 
# Serializer for Policy
class PolicySerializer(serializers.ModelSerializer):
    FrameworkCategory = serializers.CharField(source='FrameworkId.Category', read_only=True)
    FrameworkName = serializers.CharField(source='FrameworkId.FrameworkName', read_only=True)
    subpolicies = serializers.SerializerMethodField()
 
    
 
    class Meta:
        model = Policy
        fields = [
            'PolicyId', 'CurrentVersion', 'Status', 'PolicyName', 'PolicyDescription',
            'StartDate', 'EndDate', 'Department', 'CreatedByName', 'CreatedByDate',
            'Applicability', 'DocURL', 'Scope', 'Objective', 'Identifier',
            'PermanentTemporary', 'ActiveInactive', 'FrameworkId',
            'FrameworkCategory', 'FrameworkName', 'subpolicies'
        ]
 
# # Serializer for Django User (for registration/authentication)
# class UserSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = User # django.contrib.auth.models.User
#         fields = ('id', 'username', 'email', 'password')
#         extra_kwargs = {'password': {'write_only': True}}

#     def create(self, validated_data):
#         user = User.objects.create_user(
#             username=validated_data['username'],
#             email=validated_data.get('email'),
#             password=validated_data['password']
#         )
#         return user
 
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
 
# Serializer for SubPolicy
class SubPolicySerializer(serializers.ModelSerializer):
    class Meta:
        model = SubPolicy
        fields = '__all__'

# Serializer for Compliance
class ComplianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compliance
        fields = '__all__'

# Serializer for AuditFinding
class AuditFindingSerializer(serializers.ModelSerializer):
    ComplianceDetails = serializers.SerializerMethodField()
    compliance_name = serializers.SerializerMethodField()
    compliance_mitigation = serializers.SerializerMethodField()
    comments = serializers.CharField(source='Comments', required=False)

    class Meta:
        model = AuditFinding
        fields = '__all__'

    def get_ComplianceDetails(self, obj):
        if obj.ComplianceId:
            return {
                'description': obj.ComplianceId.ComplianceItemDescription,
                'mitigation': obj.ComplianceId.mitigation if hasattr(obj.ComplianceId, 'mitigation') else None,
            }
        return None

    def get_compliance_name(self, obj):
        return obj.ComplianceId.ComplianceItemDescription if obj.ComplianceId else "No description"

    def get_compliance_mitigation(self, obj):
        return obj.ComplianceId.mitigation if obj.ComplianceId and hasattr(obj.ComplianceId, 'mitigation') else None

# Serializer for Incident
class IncidentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Incident
        fields = '__all__'



class ComplianceCreateSerializer(serializers.ModelSerializer):
    SubPolicyId = serializers.PrimaryKeyRelatedField(queryset=SubPolicy.objects.all())
    Identifier = serializers.CharField(max_length=50)
    IsRisk = serializers.BooleanField()
    Criticality = serializers.ChoiceField(choices=['High', 'Medium', 'Low'])
    ManualAutomatic = serializers.ChoiceField(choices=['Manual', 'Automatic'])
    
    # Change these to CharFields to match the model
    Impact = serializers.CharField(max_length=50)
    Probability = serializers.CharField(max_length=50)
    
    ActiveInactive = serializers.ChoiceField(choices=['Active', 'Inactive'], required=False)
    PermanentTemporary = serializers.ChoiceField(choices=['Permanent', 'Temporary'])
    Status = serializers.ChoiceField(choices=['Approved', 'Active', 'Schedule', 'Rejected', 'Under Review'], required=False)
    
    class Meta:
        model = Compliance
        fields = [
            'SubPolicyId', 'Identifier', 'ComplianceItemDescription', 'IsRisk',
            'PossibleDamage', 'mitigation', 'Criticality',
            'MandatoryOptional', 'ManualAutomatic', 'Impact',
            'Probability', 'ActiveInactive', 'PermanentTemporary',
            'Status'
        ]
    
    def create(self, validated_data):
        # Auto-generate ComplianceVersion
        subpolicy = validated_data['SubPolicyId']
        latest = Compliance.objects.filter(SubPolicyId=subpolicy).order_by('-ComplianceVersion').first()
        
        if latest:
            try:
                current_version = float(latest.ComplianceVersion)
                new_version = current_version + 0.1
                validated_data['ComplianceVersion'] = f"{new_version:.1f}"
            except (ValueError, TypeError):
                validated_data['ComplianceVersion'] = "1.0"
        else:
            validated_data['ComplianceVersion'] = "1.0"
        
        return super().create(validated_data)

from .models import Risk
from .models import Incident
from .models import Compliance
from .models import RiskInstance
from .models import RiskAssignment

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

