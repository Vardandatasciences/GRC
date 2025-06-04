from rest_framework import serializers
from django.contrib.auth.models import User
from .models import Risk
from .models import Incident
from .models import Compliance
from .models import RiskInstance
from .models import RiskAssignment
from .models import GRCLog
from django.utils import timezone
from datetime import datetime, date

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
    Date = serializers.DateField(format="%Y-%m-%d", required=False)
    CreatedAt = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)
    IdentifiedAt = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", required=False)

    class Meta:
        model = Incident
        fields = '__all__'

    def get_has_risk_instance(self, obj):
        return RiskInstance.objects.filter(IncidentId=obj.IncidentId).exists()


class ComplianceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Compliance
        fields = '__all__'  # Include all fields in the model


class RiskInstanceSerializer(serializers.ModelSerializer):
    RiskMitigation = serializers.JSONField(required=False, allow_null=True)
    Date = serializers.DateField(format="%Y-%m-%d", required=False, allow_null=True)
    MitigationDueDate = serializers.DateField(format="%Y-%m-%d", required=False, allow_null=True)
    MitigationCompletedDate = serializers.DateField(format="%Y-%m-%d", required=False, allow_null=True)
    
    class Meta:
        model = RiskInstance
        fields = '__all__'
    
    def to_representation(self, instance):
        data = super().to_representation(instance)
        
        # Format date fields to string
        for field in ['Date', 'MitigationDueDate', 'MitigationCompletedDate']:
            if data.get(field):
                try:
                    # Convert to string format
                    data[field] = data[field].strftime("%Y-%m-%d") if isinstance(data[field], date) else data[field]
                except:
                    data[field] = None
        return data

    def to_internal_value(self, data):
        mutable_data = data.copy() if hasattr(data, 'copy') else dict(data)
        
        # Handle date fields
        for field in ['Date', 'MitigationDueDate', 'MitigationCompletedDate']:
            if field in mutable_data and mutable_data[field]:
                try:
                    if isinstance(mutable_data[field], str):
                        # Try to parse the date string
                        try:
                            # First try full datetime format
                            parsed_date = datetime.strptime(mutable_data[field], "%Y-%m-%d %H:%M:%S").date()
                        except ValueError:
                            try:
                                # Then try date-only format
                                parsed_date = datetime.strptime(mutable_data[field], "%Y-%m-%d").date()
                            except ValueError:
                                parsed_date = None
                        mutable_data[field] = parsed_date
                except Exception as e:
                    print(f"Error processing {field}: {e}")
                    mutable_data[field] = None
        
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


class GRCLogSerializer(serializers.ModelSerializer):
    class Meta:
        model = GRCLog
        fields = '__all__'
