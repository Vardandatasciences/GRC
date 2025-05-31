from rest_framework import serializers
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
