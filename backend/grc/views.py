from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated, IsAdminUser
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from rest_framework import viewsets
from .models import Risk
from .serializers import RiskSerializer
from .serializers import UserSerializer, RiskWorkflowSerializer
from rest_framework import viewsets
from .models import Risk, RiskAssignment
from .serializers import RiskSerializer, RiskInstanceSerializer
from .models import Incident
from .serializers import IncidentSerializer
from .models import Compliance
from .serializers import ComplianceSerializer
from .models import RiskInstance
from .serializers import RiskInstanceSerializer
from .slm_service import analyze_security_incident
from django.http import JsonResponse
from django.db.models import Count, Q
from .slm_service import analyze_security_incident
from django.contrib.auth.models import User
import datetime
import json
import traceback
from rest_framework import generics
from .models import GRCLog
from .serializers import GRCLogSerializer

# Create your views here.



import requests

LOGGING_SERVICE_URL = "http://localhost:4000/api/logs"

def send_log(module, actionType, description=None, userId=None, userName=None,
             userRole=None, entityType=None, logLevel='INFO', ipAddress=None,
             additionalInfo=None, entityId=None):
    
    # Create log entry in database
    try:
        # Prepare data for GRCLog model
        log_data = {
            'Module': module,
            'ActionType': actionType,
            'Description': description,
            'UserId': userId,
            'UserName': userName,
            'EntityType': entityType,
            'EntityId': entityId,
            'LogLevel': logLevel,
            'IPAddress': ipAddress,
            'AdditionalInfo': additionalInfo
        }
        
        # Remove None values
        log_data = {k: v for k, v in log_data.items() if v is not None}
        
        # Create and save the log entry
        log_entry = GRCLog(**log_data)
        log_entry.save()
        
        # Optionally still send to logging service if needed
        try:
            if LOGGING_SERVICE_URL:
                # Format for external service (matches expected format in loggingservice.js)
                api_log_data = {
                    "module": module,
                    "actionType": actionType,  # This is exactly what the service expects
                    "description": description,
                    "userId": userId,
                    "userName": userName,
                    "userRole": userRole,
                    "entityType": entityType,
                    "logLevel": logLevel,
                    "ipAddress": ipAddress,
                    "additionalInfo": additionalInfo
                }
                # Clean out None values
                api_log_data = {k: v for k, v in api_log_data.items() if v is not None}
                
                response = requests.post(LOGGING_SERVICE_URL, json=api_log_data)
                if response.status_code != 200:
                    print(f"Failed to send log to service: {response.text}")
        except Exception as e:
            print(f"Error sending log to service: {str(e)}")
            
        return log_entry.LogId  # Return the ID of the created log
    except Exception as e:
        print(f"Error saving log to database: {str(e)}")
        # Try to capture the error itself
        try:
            error_log = GRCLog(
                Module=module,
                ActionType='LOG_ERROR',
                Description=f"Error logging {actionType} on {module}: {str(e)}",
                LogLevel='ERROR'
            )
            error_log.save()
        except:
            pass  # If we can't even log the error, just continue
        return None


@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
    send_log(
        module="Auth",
        actionType="LOGIN",
        description="User login attempt",
        userId=None,
        userName=request.data.get('email'),
        entityType="User"
    )
    
    email = request.data.get('email')
    password = request.data.get('password')
    
    # Hardcoded credentials
    if email == "admin@example.com" and password == "password123":
        return Response({
            'success': True,
            'message': 'Login successful',
            'user': {
                'email': email,
                'name': 'Admin User'
            }
        })
    else:
        return Response({
            'success': False,
            'message': 'Invalid credentials'
        }, status=status.HTTP_401_UNAUTHORIZED)

@api_view(['POST'])
@permission_classes([AllowAny])
def register(request):
    send_log(
        module="Auth",
        actionType="REGISTER",
        description="User registration attempt",
        userId=None,
        userName=request.data.get('username', ''),
        entityType="User"
    )
    
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        refresh = RefreshToken.for_user(user)
        return Response({
            'token': str(refresh.access_token),
            'refresh': str(refresh),
            'user': serializer.data
        })
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def test_connection(request):
    send_log(
        module="System",
        actionType="TEST",
        description="API connection test",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None
    )
    
    return Response({"message": "Connection successful!"})

@api_view(['GET'])
def last_incident(request):
    send_log(
        module="Incident",
        actionType="VIEW",
        description="Viewing last incident",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="Incident"
    )
    
    last = Incident.objects.order_by('-IncidentId').first()
    if last:
        serializer = IncidentSerializer(last)
        return Response(serializer.data)
    else:
        return Response({}, status=404)

@api_view(['GET'])
def get_compliance_by_incident(request, incident_id):
    send_log(
        module="Compliance",
        actionType="VIEW",
        description=f"Viewing compliance for incident {incident_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="Compliance",
        additionalInfo={"incident_id": incident_id}
    )
    
    try:
        # Find the incident
        incident = Incident.objects.get(IncidentId=incident_id)
        
        # Find related compliance(s) where ComplianceId matches the incident's ComplianceId
        if incident.ComplianceId:
            compliance = Compliance.objects.filter(ComplianceId=incident.ComplianceId).first()
            if compliance:
                serializer = ComplianceSerializer(compliance)
                return Response(serializer.data)
        
        return Response({"message": "No related compliance found"}, status=404)
    except Incident.DoesNotExist:
        return Response({"message": "Incident not found"}, status=404)

@api_view(['GET'])
def get_risks_by_incident(request, incident_id):
    send_log(
        module="Risk",
        actionType="VIEW",
        description=f"Viewing risks for incident {incident_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="Risk",
        additionalInfo={"incident_id": incident_id}
    )
    
    try:
        # Find the incident
        incident = Incident.objects.get(IncidentId=incident_id)
        
        # Get compliance ID from the incident
        compliance_id = incident.ComplianceId
        
        if compliance_id:
            # Find all risks with the same compliance ID
            risks = Risk.objects.filter(ComplianceId=compliance_id)
            
            if risks.exists():
                serializer = RiskSerializer(risks, many=True)
                return Response(serializer.data)
        
        return Response({"message": "No related risks found"}, status=404)
    except Incident.DoesNotExist:
        return Response({"message": "Incident not found"}, status=404)

class RiskViewSet(viewsets.ModelViewSet):
    queryset = Risk.objects.all()
    serializer_class = RiskSerializer
    
    def list(self, request):
        send_log(
            module="Risk",
            actionType="LIST",
            description="Viewing all risks",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Risk"
        )
        return super().list(request)
    
    def retrieve(self, request, pk=None):
        send_log(
            module="Risk",
            actionType="VIEW",
            description=f"Viewing risk {pk}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Risk",
            additionalInfo={"risk_id": pk}
        )
        return super().retrieve(request, pk)
    
    def create(self, request):
        send_log(
            module="Risk",
            actionType="CREATE",
            description="Creating new risk",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Risk"
        )
        return super().create(request)
    
    def update(self, request, pk=None):
        send_log(
            module="Risk",
            actionType="UPDATE",
            description=f"Updating risk {pk}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Risk",
            additionalInfo={"risk_id": pk}
        )
        return super().update(request, pk)
    
    def destroy(self, request, pk=None):
        send_log(
            module="Risk",
            actionType="DELETE",
            description=f"Deleting risk {pk}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Risk",
            additionalInfo={"risk_id": pk}
        )
        return super().destroy(request, pk)

class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer
    
    def list(self, request):
        send_log(
            module="Incident",
            actionType="LIST",
            description="Viewing all incidents",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Incident"
        )
        return super().list(request)
    
    def retrieve(self, request, pk=None):
        send_log(
            module="Incident",
            actionType="VIEW",
            description=f"Viewing incident {pk}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Incident",
            additionalInfo={"incident_id": pk}
        )
        return super().retrieve(request, pk)
    
    def create(self, request):
        send_log(
            module="Incident",
            actionType="CREATE",
            description="Creating new incident",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Incident"
        )
        return super().create(request)
    
    def update(self, request, pk=None):
        send_log(
            module="Incident",
            actionType="UPDATE",
            description=f"Updating incident {pk}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Incident",
            additionalInfo={"incident_id": pk}
        )
        return super().update(request, pk)
    
    def destroy(self, request, pk=None):
        send_log(
            module="Incident",
            actionType="DELETE",
            description=f"Deleting incident {pk}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Incident",
            additionalInfo={"incident_id": pk}
        )
        return super().destroy(request, pk)

class ComplianceViewSet(viewsets.ModelViewSet):
    queryset = Compliance.objects.all()
    serializer_class = ComplianceSerializer
    lookup_field = 'ComplianceId'
    
    def list(self, request):
        send_log(
            module="Compliance",
            actionType="LIST",
            description="Viewing all compliances",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Compliance"
        )
        return super().list(request)
    
    def retrieve(self, request, ComplianceId=None):
        send_log(
            module="Compliance",
            actionType="VIEW",
            description=f"Viewing compliance {ComplianceId}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Compliance",
            additionalInfo={"compliance_id": ComplianceId}
        )
        return super().retrieve(request, ComplianceId=ComplianceId)
    
    def create(self, request):
        send_log(
            module="Compliance",
            actionType="CREATE",
            description="Creating new compliance",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Compliance"
        )
        return super().create(request)
    
    def update(self, request, ComplianceId=None):
        send_log(
            module="Compliance",
            actionType="UPDATE",
            description=f"Updating compliance {ComplianceId}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Compliance",
            additionalInfo={"compliance_id": ComplianceId}
        )
        return super().update(request, ComplianceId=ComplianceId)
    
    def destroy(self, request, ComplianceId=None):
        send_log(
            module="Compliance",
            actionType="DELETE",
            description=f"Deleting compliance {ComplianceId}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="Compliance",
            additionalInfo={"compliance_id": ComplianceId}
        )
        return super().destroy(request, ComplianceId=ComplianceId)

class RiskInstanceViewSet(viewsets.ModelViewSet):
    queryset = RiskInstance.objects.all()
    serializer_class = RiskInstanceSerializer
    
    def create(self, request, *args, **kwargs):
        # Log the create operation
        send_log(
            module="Risk",
            actionType="CREATE",
            description="Creating new risk instance",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="RiskInstance"
        )
        
        print("Original request data:", request.data)
        
        # Create a mutable dictionary for our data
        mutable_data = {}
        
        # Copy all fields except RiskMitigation, RiskOwner, and RiskStatus
        for key, value in request.data.items():
            if key not in ['RiskMitigation', 'RiskOwner', 'RiskStatus']:
                mutable_data[key] = value
        
        # Handle RiskOwner (always set to "System Owner")
        mutable_data['RiskOwner'] = "System Owner"
        
        # Handle RiskStatus (always set to "Open")
        mutable_data['RiskStatus'] = "Open"
        
        # Handle RiskMitigation - convert to proper JSON format
        if 'RiskMitigation' in request.data and request.data['RiskMitigation']:
            mitigation = request.data['RiskMitigation']
            
            # If it's already a dict, use it directly
            if isinstance(mitigation, dict):
                mutable_data['RiskMitigation'] = mitigation
            
            # If it's a string, convert to numbered JSON format
            elif isinstance(mitigation, str):
                sentences = [s.strip() for s in mitigation.split('.') if s.strip()]
                mitigation_dict = {}
                for i, sentence in enumerate(sentences, 1):
                    mitigation_dict[str(i)] = sentence
                mutable_data['RiskMitigation'] = mitigation_dict
            
            # If it's a list, use numbered format
            elif isinstance(mitigation, list):
                mitigation_dict = {}
                for i, item in enumerate(mitigation, 1):
                    mitigation_dict[str(i)] = item
                mutable_data['RiskMitigation'] = mitigation_dict
            
            # Handle case where it's already a JSON string
            elif isinstance(mitigation, str) and (mitigation.startswith('{') or mitigation.startswith('[')):
                try:
                    import json
                    mitigation_data = json.loads(mitigation)
                    mutable_data['RiskMitigation'] = mitigation_data
                except json.JSONDecodeError:
                    # If not valid JSON, create a simple entry
                    mutable_data['RiskMitigation'] = {"1": mitigation}
        else:
            # Default empty object
            mutable_data['RiskMitigation'] = {}
        
        print("Processed data:", mutable_data)
        
        # Replace the request data with our processed data
        request._full_data = mutable_data
        
        return super().create(request, *args, **kwargs)

    def update(self, request, *args, **kwargs):
        # Log the update operation
        instance = self.get_object()
        send_log(
            module="Risk",
            actionType="UPDATE",
            description=f"Updating risk instance {instance.RiskInstanceId}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="RiskInstance",
            additionalInfo={"risk_id": instance.RiskInstanceId}
        )
        
        return super().update(request, *args, **kwargs)
    
    def destroy(self, request, *args, **kwargs):
        # Log the delete operation
        instance = self.get_object()
        send_log(
            module="Risk",
            actionType="DELETE",
            description=f"Deleting risk instance {instance.RiskInstanceId}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="RiskInstance",
            additionalInfo={"risk_id": instance.RiskInstanceId}
        )
        
        return super().destroy(request, *args, **kwargs)

@api_view(['POST'])
def analyze_incident(request):
    send_log(
        module="Incident",
        actionType="ANALYZE",
        description="Analyzing incident with SLM model",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="Incident",
        additionalInfo={"title": request.data.get('title', '')}
    )
    
    incident_description = request.data.get('description', '')
    incident_title = request.data.get('title', '')
    
    # Combine title and description for better context

    print(incident_title)
    print(incident_description)
    full_incident = f"Title: {incident_title}\n\nDescription: {incident_description}"
    
    # Call the SLM function
    analysis_result = analyze_security_incident(incident_title)

    print(analysis_result)
    
    return Response(analysis_result)

def risk_metrics(request):
    # Log the metrics view
    send_log(
        module="Risk",
        actionType="VIEW",
        description="Viewing risk metrics dashboard",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskMetrics"
    )
    
    # Get the category filter parameter
    category = request.GET.get('category', '')
    
    # Base queryset
    queryset = RiskInstance.objects.all()
    
    # Apply category filter if provided
    if category:
        queryset = queryset.filter(Category__icontains=category)
    
    # Get total count after filtering by category
    total_count = queryset.count()
    
    print(f"Category filter: '{category}', Total risk instances: {total_count}")
    
    # Default counts
    open_count = 0
    in_progress_count = 0
    closed_count = 0
    
    # Let's count by looking at the filtered data
    for instance in queryset:
        status = instance.RiskStatus.lower() if instance.RiskStatus else ""
        if status == "" or status is None:
            # If status is empty, count as open by default
            open_count += 1
        elif "open" in status:
            open_count += 1
        elif "progress" in status or "in prog" in status:
            in_progress_count += 1
        elif "closed" in status or "complete" in status:
            closed_count += 1
        else:
            # Any other status, count as open
            open_count += 1
    
    # Debug info
    print(f"Filtered - Total: {total_count}, Open: {open_count}, In Progress: {in_progress_count}, Closed: {closed_count}")
    
    return JsonResponse({
        'total': total_count,
        'open': open_count,
        'inProgress': in_progress_count,
        'closed': closed_count
    })
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def get_users(request):
    send_log(
        module="User",
        actionType="VIEW",
        description="Viewing all users",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="User"
    )
    
    users = User.objects.all()
    serializer = UserSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['GET'])
def risk_workflow(request):
    """Get all risk instances for the workflow view"""
    try:
        # Fetch all risk instances
        risk_instances = RiskInstance.objects.all()
        
        # Log the view action
        send_log(
            module="Risk",
            actionType="VIEW",
            description="User viewed risk workflow",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="RiskInstance"
        )
        
        # If there are no instances, print a debug message
        if not risk_instances.exists():
            print("No risk instances found in the database")
            
        data = []
        
        for risk in risk_instances:
            # Create response data
            risk_data = {
                'RiskInstanceId': risk.RiskInstanceId,
                'RiskId': risk.RiskId,
                'RiskDescription': risk.RiskDescription,
                'Criticality': risk.Criticality,
                'Category': risk.Category,
                'RiskStatus': risk.RiskStatus,
                'RiskPriority': risk.RiskPriority,
                'RiskImpact': risk.RiskImpact,
                'MitigationDueDate': risk.MitigationDueDate,
                'MitigationStatus': risk.MitigationStatus,
                'ReviewerCount': risk.ReviewerCount or 0,
                'assignedTo': None
            }
            
            # Try to find an assignment if possible
            try:
                if risk.RiskId:
                    risk_obj = Risk.objects.filter(RiskId=risk.RiskId).first()
                    if risk_obj:
                        assignment = RiskAssignment.objects.filter(risk=risk_obj).first()
                        if assignment:
                            risk_data['assignedTo'] = assignment.assigned_to.username
            except Exception as e:
                print(f"Error checking assignment: {e}")
                
            data.append(risk_data)
        
        # Print debug info
        print(f"Returning {len(data)} risk instances")
        return Response(data)
        
    except Exception as e:
        # Log the error
        send_log(
            module="Risk",
            actionType="VIEW",
            description=f"Error viewing risk workflow: {str(e)}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="RiskInstance",
            logLevel="ERROR"
        )
        print(f"Error in risk_workflow view: {e}")
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def assign_risk_instance(request):
    """Assign a risk instance to a user from custom user table"""
    risk_id = request.data.get('risk_id')
    user_id = request.data.get('user_id')
    mitigations = request.data.get('mitigations')
    due_date = request.data.get('due_date')
    risk_form_details = request.data.get('risk_form_details')
    
    # Log the assignment request
    send_log(
        module="Risk",
        actionType="ASSIGN",
        description=f"Assigning risk {risk_id} to user {user_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskInstance",
        additionalInfo={"risk_id": risk_id, "assigned_to": user_id}
    )
    
    if not risk_id or not user_id:
        return Response({'error': 'Risk ID and User ID are required'}, status=400)
    
    try:
        # Get the risk instance
        risk_instance = RiskInstance.objects.get(RiskInstanceId=risk_id)
        
        # For custom users we don't use Django ORM
        # Just validate the user exists
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, user_name FROM grc_test.user WHERE user_id = %s", [user_id])
            user = cursor.fetchone()
        
        if not user:
            return Response({'error': 'User not found'}, status=404)
        
        # Update risk instance with assigned user
        risk_instance.RiskOwner = user[1]  # user_name
        risk_instance.UserId = user_id
        risk_instance.RiskStatus = 'Assigned'  # Update to assigned status when admin assigns
        
        # Set form details if provided
        if risk_form_details:
            risk_instance.RiskFormDetails = risk_form_details
        
        # Set mitigation due date if provided
        if due_date:
            from datetime import datetime
            try:
                # Just use the date string directly, don't convert to datetime
                risk_instance.MitigationDueDate = due_date
            except ValueError:
                print(f"Invalid date format: {due_date}")
        
        # Save mitigations if provided
        if mitigations:
            print(f"Saving mitigations to RiskMitigation field: {mitigations}")
            # Store in RiskMitigation first
            risk_instance.RiskMitigation = mitigations
            # Also copy to ModifiedMitigations
            risk_instance.ModifiedMitigations = mitigations
        
        # Set default MitigationStatus
        risk_instance.MitigationStatus = 'Yet to Start'
        
        risk_instance.save()
        print(f"Risk instance updated successfully with mitigations: {risk_instance.RiskMitigation}")
        
        # Log success or failure
        if risk_instance:
            send_log(
                module="Risk",
                actionType="ASSIGN",
                description=f"Successfully assigned risk {risk_id} to user {user_id}",
                userId=request.user.id if request.user.is_authenticated else None,
                userName=request.user.username if request.user.is_authenticated else None,
                entityType="RiskInstance",
                additionalInfo={"risk_id": risk_id, "assigned_to": user_id}
            )
            return Response({'success': True})
        else:
            send_log(
                module="Risk",
                actionType="ASSIGN",
                description=f"Failed to assign risk {risk_id}: {str(e)}",
                userId=request.user.id if request.user.is_authenticated else None,
                userName=request.user.username if request.user.is_authenticated else None,
                entityType="RiskInstance",
                logLevel="ERROR",
                additionalInfo={"risk_id": risk_id, "assigned_to": user_id}
            )
            return Response({'error': str(e)}, status=500)
    except RiskInstance.DoesNotExist:
        return Response({'error': 'Risk instance not found'}, status=404)
    except Exception as e:
        print(f"Error assigning risk: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_custom_users(request):
    """Get users from the custom user table"""
    send_log(
        module="User",
        actionType="VIEW",
        description="Viewing custom users",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="CustomUser"
    )
    
    try:
        # Using raw SQL query to fetch from your custom table
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT * FROM grc_test.user")
            columns = [col[0] for col in cursor.description]
            users = [
                dict(zip(columns, row))
                for row in cursor.fetchall()
            ]
        return Response(users)
    except Exception as e:
        print(f"Error fetching custom users: {e}")
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
def get_user_risks(request, user_id):
    """Get all risks assigned to a specific user, including completed ones"""
    try:
        # Log the view action
        send_log(
            module="Risk",
            actionType="VIEW",
            description=f"Viewing risks assigned to user {user_id}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="RiskInstance",
            additionalInfo={"viewed_user_id": user_id}
        )
        
        # Query risks that have the specific user assigned
        risk_instances = RiskInstance.objects.filter(UserId=user_id)
        
        if not risk_instances.exists():
            print(f"No risk instances found for user {user_id}")
        
        data = []
        for risk in risk_instances:
            risk_data = {
                'RiskInstanceId': risk.RiskInstanceId,
                'RiskId': risk.RiskId,
                'RiskDescription': risk.RiskDescription,
                'Criticality': risk.Criticality,
                'Category': risk.Category,
                'RiskStatus': risk.RiskStatus,
                'RiskPriority': risk.RiskPriority,
                'RiskImpact': risk.RiskImpact,
                'UserId': risk.UserId,
                'RiskOwner': risk.RiskOwner,
                'MitigationDueDate': risk.MitigationDueDate,
                'MitigationStatus': risk.MitigationStatus,
                'ReviewerCount': risk.ReviewerCount or 0
            }
            data.append(risk_data)
        
        # Sort by status - active tasks first, then completed tasks
        sorted_data = sorted(data, key=lambda x: (
            0 if x['RiskStatus'] == 'Work In Progress' else
            1 if x['RiskStatus'] == 'Under Review' else
            2 if x['RiskStatus'] == 'Revision Required' else
            3 if x['RiskStatus'] == 'Approved' else 4
        ))
        
        print(f"Returning {len(sorted_data)} risk instances for user {user_id}")
        return Response(sorted_data)
    
    except Exception as e:
        send_log(
            module="Risk",
            actionType="VIEW",
            description=f"Error viewing user risks: {str(e)}",
            userId=request.user.id if request.user.is_authenticated else None,
            userName=request.user.username if request.user.is_authenticated else None,
            entityType="RiskInstance",
            logLevel="ERROR",
            additionalInfo={"viewed_user_id": user_id}
        )
        print(f"Error fetching user risks: {e}")
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def update_risk_status(request):
    """Update the status of a risk instance"""
    risk_id = request.data.get('risk_id')
    status = request.data.get('status')
    
    # Log the status update request
    send_log(
        module="Risk",
        actionType="UPDATE",
        description=f"Updating risk {risk_id} status to {status}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskInstance",
        additionalInfo={"risk_id": risk_id, "new_status": status}
    )
    
    if not risk_id or not status:
        return Response({'error': 'Risk ID and status are required'}, status=400)
    
    try:
        # Get the risk instance
        risk_instance = RiskInstance.objects.get(RiskInstanceId=risk_id)
        
        # Update the status
        risk_instance.RiskStatus = status
        risk_instance.save()
        
        return Response({
            'success': True,
            'message': f'Risk status updated to {status}'
        })
    except RiskInstance.DoesNotExist:
        return Response({'error': 'Risk instance not found'}, status=404)
    except Exception as e:
        print(f"Error updating risk status: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_risk_mitigations(request, risk_id):
    """Get mitigation steps for a specific risk"""
    send_log(
        module="Risk",
        actionType="VIEW",
        description=f"Viewing mitigations for risk {risk_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskMitigation",
        additionalInfo={"risk_id": risk_id}
    )
    
    try:
        # Get the risk instance
        risk_instance = RiskInstance.objects.get(RiskInstanceId=risk_id)
        
        # Check if there are mitigations in the RiskMitigation field
        if not risk_instance.RiskMitigation:
            # If no specific mitigation steps, create a generic one
            mitigations = [{
                "title": "Step 1",
                "description": "No detailed mitigation workflow available.",
                "status": "Not Started"
            }]
        else:
            # Try to parse the RiskMitigation field as JSON
            try:
                # Handle string format (most common case)
                if isinstance(risk_instance.RiskMitigation, str):
                    # Parse the JSON string
                    parsed_data = json.loads(risk_instance.RiskMitigation)
                    
                    # Handle numbered object format: {"1": "Step 1", "2": "Step 2", ...}
                    if isinstance(parsed_data, dict) and all(k.isdigit() or (isinstance(k, int)) for k in parsed_data.keys()):
                        mitigations = []
                        # Sort keys numerically
                        ordered_keys = sorted(parsed_data.keys(), key=lambda k: int(k) if isinstance(k, str) else k)
                        
                        for key in ordered_keys:
                            mitigations.append({
                                "title": f"Step {key}",
                                "description": parsed_data[key],
                                "status": "Not Started"
                            })
                    # Handle array format
                    elif isinstance(parsed_data, list):
                        mitigations = parsed_data
                    # Handle other object formats
                    else:
                        mitigations = [parsed_data]
                        
                # Handle direct object format (already parsed)
                elif isinstance(risk_instance.RiskMitigation, dict):
                    parsed_data = risk_instance.RiskMitigation
                    # Handle numbered object
                    if all(k.isdigit() or (isinstance(k, int)) for k in parsed_data.keys()):
                        mitigations = []
                        ordered_keys = sorted(parsed_data.keys(), key=lambda k: int(k) if isinstance(k, str) else k)
                        
                        for key in ordered_keys:
                            mitigations.append({
                                "title": f"Step {key}",
                                "description": parsed_data[key],
                                "status": "Not Started"
                            })
                    else:
                        mitigations = [parsed_data]
                        
                # Handle direct array format
                elif isinstance(risk_instance.RiskMitigation, list):
                    mitigations = risk_instance.RiskMitigation
                    
                # Handle unexpected format
                else:
                    mitigations = [{
                        "title": "Step 1",
                        "description": str(risk_instance.RiskMitigation),
                        "status": "Not Started"
                    }]
                    
            except json.JSONDecodeError:
                # If it's not valid JSON, create a single step with the text
                mitigations = [{
                    "title": "Step 1",
                    "description": risk_instance.RiskMitigation,
                    "status": "Not Started"
                }]
            except Exception as e:
                print(f"Error parsing mitigations: {e}")
                mitigations = [{
                    "title": "Step 1",
                    "description": f"Error parsing mitigation data: {str(e)}",
                    "status": "Error"
                }]
        
        # Add default fields if they're missing
        for i, step in enumerate(mitigations):
            if "title" not in step:
                step["title"] = f"Step {i+1}"
            if "description" not in step:
                step["description"] = "No description provided"
            if "status" not in step:
                step["status"] = "Not Started"
            # Set locked state based on previous steps
            step["locked"] = i > 0  # All steps except first are initially locked
        
        return Response(mitigations)
    
    except RiskInstance.DoesNotExist:
        return Response([{
            "title": "Error",
            "description": "Risk instance not found",
            "status": "Error"
        }], status=404)
    except Exception as e:
        print(f"Error fetching risk mitigations: {e}")
        return Response([{
            "title": "Error",
            "description": f"Server error: {str(e)}",
            "status": "Error"
        }], status=500)

@api_view(['POST'])
def update_mitigation_approval(request):
    """Update the approval status of a mitigation step"""
    approval_id = request.data.get('approval_id')
    mitigation_id = request.data.get('mitigation_id')
    approved = request.data.get('approved')
    remarks = request.data.get('remarks', '')
    
    send_log(
        module="Risk",
        actionType="APPROVE_MITIGATION",
        description=f"Updating mitigation approval for risk {approval_id}, mitigation {mitigation_id}, approved: {approved}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskMitigation",
        additionalInfo={"approval_id": approval_id, "mitigation_id": mitigation_id, "approved": approved}
    )
    
    if not approval_id or not mitigation_id:
        return Response({'error': 'Approval ID and mitigation ID are required'}, status=400)
    
    try:
        # Get the latest approval record by RiskInstanceId
        from django.db import connection
        with connection.cursor() as cursor:
            # Get the latest version for this risk
            cursor.execute("""
                SELECT ra.ExtractedInfo, ra.UserId, ra.ApproverId, ra.version 
                FROM grc_test.risk_approval ra
                WHERE ra.RiskInstanceId = %s
                ORDER BY 
                    CASE 
                        WHEN ra.version LIKE 'U%_update%' THEN 1
                        WHEN ra.version LIKE 'U%' THEN 2
                        WHEN ra.version LIKE 'R%_update%' THEN 3
                        WHEN ra.version LIKE 'R%' THEN 4
                        ELSE 5
                    END,
                    ra.version DESC
                LIMIT 1
            """, [approval_id])
            row = cursor.fetchone()
            
            if not row:
                return Response({'error': 'Approval record not found'}, status=404)
            
            import json
            extracted_info, user_id, approver_id, current_version = row[0], row[1], row[2], row[3]
            extracted_info_dict = json.loads(extracted_info)
            
            # Create a working copy to modify
            if 'mitigations' in extracted_info_dict and mitigation_id in extracted_info_dict['mitigations']:
                extracted_info_dict['mitigations'][mitigation_id]['approved'] = approved
                extracted_info_dict['mitigations'][mitigation_id]['remarks'] = remarks
                
                # Create an interim update version
                # If version already has _update suffix, don't add it again
                update_version = current_version + "_update" if "_update" not in current_version else current_version
                
                # Insert a new record with the interim version
                cursor.execute("""
                    INSERT INTO grc_test.risk_approval 
                    (RiskInstanceId, version, ExtractedInfo, UserId, ApproverId)
                    VALUES (%s, %s, %s, %s, %s)
                """, [
                    approval_id,
                    update_version,
                    json.dumps(extracted_info_dict),
                    user_id,
                    approver_id
                ])
                
                return Response({
                    'success': True,
                    'message': f'Mitigation {mitigation_id} approval status updated'
                })
            else:
                return Response({'error': 'Mitigation ID not found in approval record'}, status=404)
    except Exception as e:
        print(f"Error updating mitigation approval: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['POST'])
def assign_reviewer(request):
    """Assign a reviewer to a risk instance and create approval record"""
    risk_id = request.data.get('risk_id')
    reviewer_id = request.data.get('reviewer_id')
    user_id = request.data.get('user_id')  # Current user/assigner ID
    mitigations = request.data.get('mitigations')  # Get mitigation data with status
    risk_form_details = request.data.get('risk_form_details', None)  # Get form details
    
    # Log the reviewer assignment
    send_log(
        module="Risk",
        actionType="ASSIGN_REVIEWER",
        description=f"Assigning reviewer {reviewer_id} to risk {risk_id}",
        userId=user_id,
        entityType="RiskApproval",
        additionalInfo={"risk_id": risk_id, "reviewer_id": reviewer_id}
    )
    
    if not risk_id or not reviewer_id or not user_id:
        return Response({'error': 'Risk ID, reviewer ID, and user ID are required'}, status=400)
    
    try:
        # Get the risk instance
        risk_instance = RiskInstance.objects.get(RiskInstanceId=risk_id)
        
        # Update form details if provided
        if risk_form_details:
            risk_instance.RiskFormDetails = risk_form_details
        
        # Validate reviewer exists
        from django.db import connection
        with connection.cursor() as cursor:
            cursor.execute("SELECT user_id, user_name FROM grc_test.user WHERE user_id = %s", [reviewer_id])
            reviewer = cursor.fetchone()
        
        if not reviewer:
            return Response({'error': 'Reviewer not found'}, status=404)
        
        # Update the risk instance status
        risk_instance.RiskStatus = 'Assigned'  # Keep as assigned
        risk_instance.MitigationStatus = 'Revision Required by Reviewer'  # User submitted, needs reviewer
        
        # Initialize ReviewerCount if it's None
        if risk_instance.ReviewerCount is None:
            risk_instance.ReviewerCount = 0
            
        # Increment reviewer count when assigning a reviewer
        risk_instance.ReviewerCount += 1
        
        risk_instance.save()
        
        # Determine the next version number (U1, U2, etc.)
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT version FROM grc_test.risk_approval 
                WHERE RiskInstanceId = %s AND version LIKE 'U%%'
                ORDER BY CAST(SUBSTRING(version, 2) AS UNSIGNED) DESC
                LIMIT 1
            """, [risk_id])
            row = cursor.fetchone()
            
            if not row or not row[0]:
                version = "U1"  # First user submission
            else:
                current_version = row[0]
                # Extract number part and increment
                if current_version.startswith('U'):
                    try:
                        number = int(current_version[1:])
                        version = f"U{number + 1}"
                    except ValueError:
                        version = "U1"
                else:
                    version = "U1"  # Fallback to U1
        
        # Create a simplified JSON structure for ExtractedInfo
        import json
        
        # Use the mitigation data provided, or get from the risk instance
        mitigation_steps = {}
        if mitigations:
            # Use the provided mitigations data but don't set 'approved' field for initial submission
            is_first_submission = version == "U1"
            
            for key, value in mitigations.items():
                mitigation_steps[key] = {
                    "description": value["description"],
                    "status": value["status"] if "status" in value else "Completed",
                    "comments": value.get("comments", ""),
                    "fileData": value.get("fileData", None),
                    "fileName": value.get("fileName", None)
                }
                
                # Only set approved field if this is not the first submission or the value is coming from a previous approval
                if not is_first_submission or "approved" in value and value["approved"] is True:
                    mitigation_steps[key]["approved"] = value["approved"]
                    mitigation_steps[key]["remarks"] = value.get("remarks", "")
        
        # Create the simplified JSON structure
        extracted_info = {
            "risk_id": risk_id,
            "mitigations": mitigation_steps,
            "version": version,
            "submission_date": datetime.datetime.now().isoformat(),
            "risk_form_details": risk_form_details  # Add form details to ExtractedInfo
        }
        
        # Insert into risk_approval table with ApprovedRejected as NULL for new submissions
        with connection.cursor() as cursor:
            cursor.execute(
                """
                INSERT INTO grc_test.risk_approval 
                (RiskInstanceId, version, ExtractedInfo, UserId, ApproverId, ApprovedRejected)
                VALUES (%s, %s, %s, %s, %s, NULL)
                """,
                [
                    risk_id,
                    version,  # Use the version we calculated
                    json.dumps(extracted_info),
                    user_id,
                    reviewer_id
                ]
            )
        
        return Response({
            'success': True,
            'message': f'Reviewer {reviewer[1]} assigned to risk and approval record created with version {version}'
        })
    except RiskInstance.DoesNotExist:
        return Response({'error': 'Risk instance not found'}, status=404)
    except Exception as e:
        print(f"Error assigning reviewer: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_reviewer_tasks(request, user_id):
    """Get all risks where the user is assigned as a reviewer, including completed ones"""
    send_log(
        module="Risk",
        actionType="VIEW",
        description=f"Viewing reviewer tasks for user {user_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskReview",
        additionalInfo={"reviewer_id": user_id}
    )
    
    try:
        # Using raw SQL query to fetch from approval table
        from django.db import connection
        with connection.cursor() as cursor:
            # Modified query to get only the latest version for each risk
            cursor.execute("""
                WITH latest_versions AS (
                    SELECT ra.RiskInstanceId, MAX(ra.version) as latest_version
                    FROM grc_test.risk_approval ra
                    WHERE ra.ApproverId = %s
                    GROUP BY ra.RiskInstanceId
                )
                SELECT ra.RiskInstanceId, ra.ExtractedInfo, ra.UserId, ra.ApproverId, ra.version,
                       ri.RiskDescription, ri.Criticality, ri.Category, ri.RiskStatus, ri.RiskPriority 
                FROM grc_test.risk_approval ra
                JOIN latest_versions lv ON ra.RiskInstanceId = lv.RiskInstanceId AND ra.version = lv.latest_version
                JOIN grc_test.risk_instance ri ON ra.RiskInstanceId = ri.RiskInstanceId
                WHERE ra.ApproverId = %s
                ORDER BY 
                    CASE 
                        WHEN ri.RiskStatus = 'Under Review' THEN 1
                        WHEN ri.RiskStatus = 'Revision Required' THEN 2
                        WHEN ri.RiskStatus = 'Work In Progress' THEN 3
                        WHEN ri.RiskStatus = 'Approved' THEN 4
                        ELSE 5
                    END,
                    ra.RiskInstanceId
            """, [user_id, user_id])
            columns = [col[0] for col in cursor.description]
            reviewer_tasks = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        return Response(reviewer_tasks)
    except Exception as e:
        print(f"Error fetching reviewer tasks: {e}")
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def complete_review(request):
    """Complete the review process for a risk"""
    import json
    import datetime
    import traceback
    
    # Log the review completion
    
    
    try:
        # Print request data for debugging
        print("Complete review request data:", request.data)
        
        approval_id = request.data.get('approval_id')  # This is RiskInstanceId
        risk_id = request.data.get('risk_id')
        approved = request.data.get('approved')
        mitigations = request.data.get('mitigations', {})  # Get all mitigations
        risk_form_details = request.data.get('risk_form_details', None)  # Get form details
        
        # Make sure we have the necessary data
        if not risk_id:
            print("Missing risk_id in request data")
            return Response({'error': 'Risk ID is required'}, status=400)
            
        # Set approval_id to risk_id if it's missing
        if not approval_id:
            approval_id = risk_id
        
        # Get the risk instance to update statuses
        risk_instance = RiskInstance.objects.get(RiskInstanceId=risk_id)
        
        # Update risk form details if approved
        if approved and risk_form_details:
            risk_instance.RiskFormDetails = risk_form_details
        
        # Update risk status based on approval
        if approved:
            risk_instance.RiskStatus = 'Approved'
            risk_instance.MitigationStatus = 'Completed'
            # No need to increment reviewer count as this is the final approval
        else:
            risk_instance.RiskStatus = 'Assigned'  # Keep as assigned
            risk_instance.MitigationStatus = 'Revision Required by User'  # Reviewer submitted, needs user revision
            
            # Increment reviewer count only if not yet approved
            if risk_instance.ReviewerCount is None:
                risk_instance.ReviewerCount = 1
            else:
                risk_instance.ReviewerCount += 1
        
        risk_instance.save()
        
        # Get current approval record to get relevant data
        from django.db import connection
        with connection.cursor() as cursor:
            # Get the latest version
            cursor.execute("""
                SELECT ExtractedInfo, UserId, ApproverId, version
                FROM grc_test.risk_approval
                WHERE RiskInstanceId = %s
                ORDER BY version DESC
                LIMIT 1
            """, [risk_id])
            
            row = cursor.fetchone()
            if not row:
                return Response({'error': 'Approval record not found'}, status=404)
                
            extracted_info, user_id, approver_id, current_version = row[0], row[1], row[2], row[3]
            
            # Determine the next R version
            cursor.execute("""
                SELECT version FROM grc_test.risk_approval 
                WHERE RiskInstanceId = %s AND version LIKE 'R%%'
                ORDER BY version DESC
                LIMIT 1
            """, [risk_id])
            
            row = cursor.fetchone()
            
            if not row or not row[0]:
                # First reviewer version
                new_version = "R1"
            else:
                # Get the next reviewer version
                current_r_version = row[0]
                try:
                    # Extract the number part
                    number = int(current_r_version[1:])
                    new_version = f"R{number + 1}"
                except ValueError:
                    new_version = "R1"
            
            # Create the new data structure directly matching your desired format
            extracted_info_dict = json.loads(extracted_info)
            
            # Build the new JSON structure with the exact format you want
            new_json = {
                "risk_id": int(risk_id) if isinstance(risk_id, str) and risk_id.isdigit() else risk_id,
                "version": new_version,
                "mitigations": {},
                "review_date": datetime.datetime.now().isoformat(),
                "overall_approved": approved,
                "risk_form_details": risk_form_details or extracted_info_dict.get("risk_form_details", {})  # Include form details
            }
            
            # Copy the mitigations from the request
            for mitigation_id, mitigation_data in mitigations.items():
                # Include file data and comments in the stored JSON
                new_json["mitigations"][mitigation_id] = {
                    "description": mitigation_data["description"],
                    "approved": mitigation_data["approved"],
                    "remarks": mitigation_data["remarks"] if not mitigation_data["approved"] else "",
                    "comments": mitigation_data.get("comments", ""),
                    "fileData": mitigation_data.get("fileData", None),
                    "fileName": mitigation_data.get("fileName", None)
                }
            
            # Insert new record with the R version and set ApprovedRejected column
            cursor.execute("""
                INSERT INTO grc_test.risk_approval 
                (RiskInstanceId, version, ExtractedInfo, UserId, ApproverId, ApprovedRejected)
                VALUES (%s, %s, %s, %s, %s, %s)
            """, [
                risk_id,
                new_version,
                json.dumps(new_json),
                user_id,
                approver_id,
                "Approved" if approved else "Rejected"
            ])
            
            # Update the risk status based on approval
            risk_status = 'Approved' if approved else 'Revision Required'
            cursor.execute("""
                UPDATE grc_test.risk_instance
                SET RiskStatus = %s
                WHERE RiskInstanceId = %s
            """, [risk_status, risk_id])


        send_log(
        module="Risk",
        actionType="COMPLETE_REVIEW",
        description=f"Completing review for risk {risk_id} with status: {'Approved' if approved else 'Rejected'}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskApproval",
        additionalInfo={"risk_id": risk_id, "approved": approved}
    )
            
        return Response({
            'success': True,
            'message': f'Review completed and risk status updated to {risk_status} with version {new_version}'
        })
    except Exception as e:
        print(f"Error completing review: {e}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_user_notifications(request, user_id):
    """Get notifications for the user about their reviewed tasks"""
    send_log(
        module="Risk",
        actionType="VIEW",
        description=f"Viewing notifications for user {user_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="Notification",
        additionalInfo={"user_id": user_id}
    )
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Get the latest R version for each risk submitted by this user
            cursor.execute("""
                WITH latest_r_versions AS (
                    SELECT ra.RiskInstanceId, MAX(ra.version) as latest_version
                    FROM grc_test.risk_approval ra
                    WHERE ra.UserId = %s 
                    AND ra.version LIKE 'R%'
                    AND ra.version NOT LIKE '%update%'
                    GROUP BY ra.RiskInstanceId
                )
                SELECT ra.RiskInstanceId, ra.ExtractedInfo, ra.version,
                       ri.RiskDescription, ri.RiskStatus
                FROM grc_test.risk_approval ra
                JOIN latest_r_versions lrv ON ra.RiskInstanceId = lrv.RiskInstanceId AND ra.version = lrv.latest_version
                JOIN grc_test.risk_instance ri ON ra.RiskInstanceId = ri.RiskInstanceId
                WHERE ra.UserId = %s
            """, [user_id, user_id])
            columns = [col[0] for col in cursor.description]
            notifications = []
            
            for row in cursor.fetchall():
                data = dict(zip(columns, row))
                
                # Extract approval info
                extracted_info = json.loads(data['ExtractedInfo'])
                overall_approved = extracted_info.get('overall_approved', None)
                
                # Add approval status info
                data['approved'] = overall_approved
                notifications.append(data)
            
        return Response(notifications)
    except Exception as e:
        print(f"Error fetching user notifications: {e}")
        return Response({"error": str(e)}, status=500)

@api_view(['POST'])
def update_mitigation_status(request):
    """Update the mitigation status of a risk instance"""
    risk_id = request.data.get('risk_id')
    status = request.data.get('status')
    
    send_log(
        module="Risk",
        actionType="UPDATE",
        description=f"Updating mitigation status for risk {risk_id} to {status}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskMitigation",
        additionalInfo={"risk_id": risk_id, "status": status}
    )
    
    # Debug information
    print(f"Received update_mitigation_status request: risk_id={risk_id}, status={status}")
    print(f"Request data: {request.data}")
    
    if not risk_id:
        return Response({'error': 'Risk ID is required'}, status=400)
    
    if not status:
        return Response({'error': 'Status is required'}, status=400)
    
    try:
        # Get the risk instance
        risk_instance = RiskInstance.objects.get(RiskInstanceId=risk_id)
        
        # Update the mitigation status
        risk_instance.MitigationStatus = status
        
        # If status is completed, also update risk status to approved
        if status == 'Completed':
            risk_instance.RiskStatus = 'Approved'
        
        risk_instance.save()
        print(f"Successfully updated risk {risk_id} mitigation status to {status}")
        
        return Response({
            'success': True,
            'message': f'Mitigation status updated to {status}'
        })
    except RiskInstance.DoesNotExist:
        print(f"Error: Risk instance with ID {risk_id} not found")
        return Response({'error': 'Risk instance not found'}, status=404)
    except Exception as e:
        print(f"Error updating mitigation status: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_reviewer_comments(request, risk_id):
    """Get reviewer comments for rejected mitigations"""
    send_log(
        module="Risk",
        actionType="VIEW",
        description=f"Viewing reviewer comments for risk {risk_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskReview",
        additionalInfo={"risk_id": risk_id}
    )
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Get the latest R version for this risk
            cursor.execute("""
                SELECT ra.ExtractedInfo
                FROM grc_test.risk_approval ra
                WHERE ra.RiskInstanceId = %s 
                AND ra.version LIKE 'R%%'
                ORDER BY version DESC
                LIMIT 1
            """, [risk_id])
            
            row = cursor.fetchone()
            if not row:
                return Response({}, status=404)
            
            import json
            extracted_info = json.loads(row[0])
            
            comments = {}
            if 'mitigations' in extracted_info:
                for mitigation_id, mitigation_data in extracted_info['mitigations'].items():
                    # Only include rejected mitigations with remarks
                    if mitigation_data.get('approved') is False and mitigation_data.get('remarks'):
                        comments[mitigation_id] = mitigation_data['remarks']
            
            return Response(comments)
    except Exception as e:
        print(f"Error fetching reviewer comments: {e}")
        traceback.print_exc()
        return Response({"error": str(e)}, status=500)

@api_view(['GET'])
def get_latest_review(request, risk_id):
    """Get the latest review data for a risk (latest R version)"""
    send_log(
        module="Risk",
        actionType="VIEW",
        description=f"Viewing latest review for risk {risk_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskReview",
        additionalInfo={"risk_id": risk_id}
    )
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Get the latest R version of review data
            cursor.execute("""
                SELECT ExtractedInfo
                FROM grc_test.risk_approval
                WHERE RiskInstanceId = %s AND version LIKE 'R%%'
                ORDER BY 
                    CAST(SUBSTRING(version, 2) AS UNSIGNED) DESC
                LIMIT 1
            """, [risk_id])
            
            row = cursor.fetchone()
            if not row:
                # If no review found, return empty object
                return Response({})
            
            import json
            extracted_info = json.loads(row[0])
            print(extracted_info)
            return Response(extracted_info)
    except Exception as e:
        print(f"Error fetching latest review: {e}")
        traceback.print_exc()
        # Return empty object instead of error in case of exception
        return Response({})

@api_view(['GET'])
def get_assigned_reviewer(request, risk_id):
    """Get the assigned reviewer for a risk from the risk_approval table"""
    send_log(
        module="Risk",
        actionType="VIEW",
        description=f"Viewing assigned reviewer for risk {risk_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskReview",
        additionalInfo={"risk_id": risk_id}
    )
    
    try:
        from django.db import connection
        with connection.cursor() as cursor:
            # Get the ApproverId from any version (they should all have the same reviewer)
            cursor.execute("""
                SELECT ApproverId, user_name 
                FROM grc_test.risk_approval ra
                JOIN grc_test.user u ON ra.ApproverId = u.user_id
                WHERE ra.RiskInstanceId = %s
                LIMIT 1
            """, [risk_id])
            
            row = cursor.fetchone()
            if not row:
                return Response({}, status=200)  # Return empty object with 200 status instead of 404
            
            return Response({
                'reviewer_id': row[0],
                'reviewer_name': row[1]
            })
    except Exception as e:
        print(f"Error fetching assigned reviewer: {e}")
        # Return empty object with 200 status instead of error
        return Response({}, status=200)

@api_view(['PUT'])
def update_risk_mitigation(request, risk_id):
    """Update the mitigation steps for a risk instance"""
    mitigation_data = request.data.get('mitigation_data')
    
    # Log the mitigation update
    send_log(
        module="Risk",
        actionType="UPDATE_MITIGATION",
        description=f"Updating mitigation data for risk {risk_id}",
        userId=request.user.id if request.user.is_authenticated else None,
        userName=request.user.username if request.user.is_authenticated else None,
        entityType="RiskInstance",
        additionalInfo={"risk_id": risk_id}
    )
    
    if not mitigation_data:
        return Response({'error': 'Mitigation data is required'}, status=400)
    
    try:
        # Get the risk instance
        risk_instance = RiskInstance.objects.get(RiskInstanceId=risk_id)
        
        # Only update the ModifiedMitigations field, keep RiskMitigation unchanged
        risk_instance.ModifiedMitigations = mitigation_data
        risk_instance.save()
        
        return Response({
            'success': True,
            'message': 'Modified mitigation data updated successfully'
        })
    except RiskInstance.DoesNotExist:
        return Response({'error': 'Risk instance not found'}, status=404)
    except Exception as e:
        print(f"Error updating modified mitigation: {e}")
        return Response({'error': str(e)}, status=500)

@api_view(['GET'])
def get_risk_form_details(request, risk_id):
    """Get form details for a risk instance"""
    try:
        risk_instance = RiskInstance.objects.get(RiskInstanceId=risk_id)
        form_details = risk_instance.RiskFormDetails
        
        # If no form details exist, return default empty structure
        if not form_details:
            form_details = {
                "cost": "",
                "impact": "",
                "financialImpact": "",
                "reputationalImpact": ""
            }
        
        return Response(form_details)
    except RiskInstance.DoesNotExist:
        return Response({"error": "Risk instance not found"}, status=404)
    except Exception as e:
        print(f"Error fetching risk form details: {e}")
        return Response({"error": str(e)}, status=500)

class GRCLogList(generics.ListCreateAPIView):
    queryset = GRCLog.objects.all().order_by('-Timestamp')
    serializer_class = GRCLogSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        queryset = GRCLog.objects.all().order_by('-Timestamp')
        
        # Filter by module if provided
        module = self.request.query_params.get('module')
        if module:
            queryset = queryset.filter(Module__icontains=module)
            
        # Filter by action type if provided
        action_type = self.request.query_params.get('action_type')
        if action_type:
            queryset = queryset.filter(ActionType__icontains=action_type)
            
        # Filter by entity type if provided
        entity_type = self.request.query_params.get('entity_type')
        if entity_type:
            queryset = queryset.filter(EntityType__icontains=entity_type)
            
        # Filter by log level if provided
        log_level = self.request.query_params.get('log_level')
        if log_level:
            queryset = queryset.filter(LogLevel__iexact=log_level)
            
        # Filter by user if provided
        user_id = self.request.query_params.get('user_id')
        if user_id:
            queryset = queryset.filter(UserId=user_id)
            
        # Filter by date range if provided
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date and end_date:
            queryset = queryset.filter(Timestamp__range=[start_date, end_date])
            
        return queryset

class GRCLogDetail(generics.RetrieveAPIView):
    queryset = GRCLog.objects.all()
    serializer_class = GRCLogSerializer
    permission_classes = [IsAuthenticated]
