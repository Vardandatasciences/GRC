from django.shortcuts import render, redirect
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer, IncidentSerializer, AuditFindingsSerializer, UsersSerializer, WorkflowSerializer
from .models import Incident, AuditFindings, Users, Workflow
from django.views.decorators.csrf import csrf_exempt

# Create your views here.

LOGIN_REDIRECT_URL = '/incidents/'  # or the URL pattern for your incident page

@api_view(['POST'])
@permission_classes([AllowAny])
def login(request):
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
@permission_classes([AllowAny])
def list_incidents(request):
    incidents = Incident.objects.all()
    serializer = IncidentSerializer(incidents, many=True)
    return Response(serializer.data)

@csrf_exempt
@api_view(['POST'])
@permission_classes([AllowAny])
def create_incident(request):
    serializer = IncidentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

def login_view(request):
    # ... your login logic ...
    if user_is_authenticated:
        return redirect('incident_page')  # Use your URL name or path

def incident_page(request):
    # Optionally fetch and pass incidents to the template
    return render(request, 'incidents.html')

# def create_incident(request):
#     if request.method == 'POST':
#         # Handle form submission and create incident
#         pass
#     return render(request, 'create_incident.html')

@api_view(['GET'])
@permission_classes([AllowAny])
def unchecked_audit_findings(request):
    findings = AuditFindings.objects.filter(check_status='0')
    serializer = AuditFindingsSerializer(findings, many=True)
    return Response(serializer.data)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_users(request):
    users = Users.objects.all()
    serializer = UsersSerializer(users, many=True)
    return Response(serializer.data)

@api_view(['POST'])
@permission_classes([AllowAny])
def create_workflow(request):
    data = request.data.copy()
    # Accept either finding_id or IncidentId
    finding_id = data.get('finding_id')
    incident_id = data.get('incident_id') or data.get('IncidentId')

    if not data.get('assignee_id') or not data.get('reviewer_id') or (not finding_id and not incident_id):
        return Response({'error': 'Missing required fields'}, status=status.HTTP_400_BAD_REQUEST)

    # Set the correct fields for the serializer
    if finding_id:
        data['finding_id'] = finding_id
        data['IncidentId'] = None
    else:
        data['IncidentId'] = incident_id
        data['finding_id'] = None

    serializer = WorkflowSerializer(data=data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_assigned_findings(request):
    workflows = Workflow.objects.all()
    result = []
    for wf in workflows:
        # Assigned Audit Finding
        if wf.finding_id:
            try:
                finding = AuditFindings.objects.get(date=wf.finding_id)
                result.append({
                    'type': 'finding',
                    'date': wf.finding_id,
                    'comment': finding.comment,
                    'assignee': Users.objects.get(UserId=wf.assignee_id).UserName,
                    'reviewer': Users.objects.get(UserId=wf.reviewer_id).UserName,
                    'assigned_at': wf.assigned_at,
                })
            except AuditFindings.DoesNotExist:
                continue
        # Assigned Incident
        elif wf.IncidentId:
            try:
                incident = Incident.objects.get(IncidentId=wf.IncidentId)
                result.append({
                    'type': 'incident',
                    'IncidentId': wf.IncidentId,
                    'incidenttitle': incident.incidenttitle,
                    'description': incident.description,
                    'assignee': Users.objects.get(UserId=wf.assignee_id).UserName,
                    'reviewer': Users.objects.get(UserId=wf.reviewer_id).UserName,
                    'assigned_at': wf.assigned_at,
                })
            except Incident.DoesNotExist:
                continue
    return Response(result)
