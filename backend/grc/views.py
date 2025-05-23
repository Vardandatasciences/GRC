from django.shortcuts import render, redirect, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import (
    UserSerializer, IncidentSerializer, AuditFindingSerializer, UsersSerializer, WorkflowSerializer,
    PolicySerializer, SubPolicySerializer, ComplianceCreateSerializer
)
from .models import Incident, AuditFinding, Users, Workflow, Compliance, Framework, PolicyVersion, PolicyApproval, Policy, SubPolicy
from django.views.decorators.csrf import csrf_exempt
from django.db import transaction
import traceback
import datetime
from django.db import connection
import json
import uuid
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
    print("Received data:", request.data)
    serializer = IncidentSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    print("Serializer errors:", serializer.errors)
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
    findings = AuditFinding.objects.filter(check_status='0')
    serializer = AuditFindingSerializer(findings, many=True)
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
                finding = AuditFinding.objects.get(date=wf.finding_id)
                result.append({
                    'type': 'finding',
                    'date': wf.finding_id,
                    'comment': finding.comment,
                    'assignee': Users.objects.get(UserId=wf.assignee_id).UserName,
                    'reviewer': Users.objects.get(UserId=wf.reviewer_id).UserName,
                    'assigned_at': wf.assigned_at,
                })
            except AuditFinding.DoesNotExist:
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

@api_view(['GET'])
@permission_classes([AllowAny])
def combined_incidents_and_audit_findings(request):
    # Get all incidents from the database
    all_incidents = Incident.objects.all()
    all_incidents_serialized = IncidentSerializer(all_incidents, many=True).data
    
    # Categorize by type
    for item in all_incidents_serialized:
        if item['Origin'] == 'Manual':
            item['type'] = 'manual'
            item['source'] = 'manual'
        elif item['Origin'] == 'Audit Finding':
            item['type'] = 'audit_incident'
            item['source'] = 'auditor'
            # Add criticality for audit incidents
            if item['ComplianceId']:
                try:
                    compliance = Compliance.objects.get(pk=item['ComplianceId'])
                    item['criticality'] = compliance.Criticality if hasattr(compliance, 'Criticality') else None
                except Compliance.DoesNotExist:
                    item['criticality'] = None
        elif item['Origin'] == 'SIEM':
            item['type'] = 'siem'
            item['source'] = 'siem'
        else:
            item['type'] = 'other'
            item['source'] = 'other'
    
    # Get audit findings with Check='0' or Check='2'
    audit_findings = AuditFinding.objects.filter(Check__in=['0', '2'])
    audit_findings_serialized = AuditFindingSerializer(audit_findings, many=True).data
    
    # Process each audit finding
    for item in audit_findings_serialized:
        item['type'] = 'audit'
        item['Origin'] = 'Audit Finding'  # Set origin for filtering in frontend
        item['source'] = 'auditor'  # All audit findings come from auditor
        
        # Get the complete compliance item details
        if item['ComplianceId']:
            try:
                compliance = Compliance.objects.get(pk=item['ComplianceId'])
                item['compliance_name'] = compliance.ComplianceItemDescription
                item['compliance_mitigation'] = compliance.mitigation if hasattr(compliance, 'mitigation') else None
                item['criticality'] = compliance.Criticality if hasattr(compliance, 'Criticality') else None
            except Compliance.DoesNotExist:
                item['compliance_name'] = "No description"
                item['compliance_mitigation'] = None
                item['criticality'] = None
        else:
            item['compliance_name'] = "No description"
            item['compliance_mitigation'] = None
            item['criticality'] = None
                
        # Check if there's a corresponding incident
        related_incident = None
        if item['AuditId'] and item['ComplianceId']:
            related_incident = Incident.objects.filter(
                Origin="Audit Finding",
                AuditId=item['AuditId'],
                ComplianceId=item['ComplianceId']
            ).first()
        
        if related_incident:
            item['Status'] = related_incident.Status
        else:
            item['Status'] = None
    
    combined = all_incidents_serialized + audit_findings_serialized
    return Response(combined)

@api_view(['POST'])
def create_incident_from_audit_finding(request):
    finding_id = request.data.get('audit_finding_id')

    try:
        finding = AuditFinding.objects.get(pk=finding_id)
    except AuditFinding.DoesNotExist:
        return Response({'error': 'Audit finding not found'}, status=status.HTTP_404_NOT_FOUND)

    # Check if an incident already exists for this finding
    existing_incident = Incident.objects.filter(
        Origin="Audit Finding",
        AuditId=finding.AuditId,
        ComplianceId=finding.ComplianceId
    ).first()
    
    if existing_incident:
        # Update the existing incident
        existing_incident.Status = 'Scheduled'
        existing_incident.save()
        serializer = IncidentSerializer(existing_incident)
        return Response(serializer.data, status=status.HTTP_200_OK)

    # Create a new incident
    incident_data = {
        'IncidentTitle': finding.ComplianceId.ComplianceItemDescription if finding.ComplianceId else "Audit Finding",
        'Description': finding.DetailsOfFinding or finding.Comments or "",
        'Mitigation': finding.ComplianceId.mitigation if finding.ComplianceId else "",
        'AuditId': finding.AuditId.pk if finding.AuditId else None,
        'ComplianceId': finding.ComplianceId.pk if finding.ComplianceId else None,
        'Date': finding.AssignedDate.date() if finding.AssignedDate else None,
        'Time': finding.AssignedDate.time() if finding.AssignedDate else None,
        'UserId': finding.UserId.UserId,
        'Origin': 'Audit Finding',
        'Comments': finding.Comments,
        'Status': 'Scheduled',
    }

    serializer = IncidentSerializer(data=incident_data)
    if serializer.is_valid():
        incident = serializer.save()
        # Do not change the Check status if it's partially compliant (2)
        if finding.Check != '2':
            finding.Check = '1'  # Mark as compliant/processed
            finding.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    else:
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def schedule_manual_incident(request):
    incident_id = request.data.get('incident_id')
    try:
        incident = Incident.objects.get(pk=incident_id, Origin="Manual")
        incident.Status = "Scheduled"
        incident.save()
        return Response({'message': 'Incident scheduled and directed to risk workflow.'}, status=status.HTTP_200_OK)
    except Incident.DoesNotExist:
        return Response({'error': 'Incident not found.'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
def reject_incident(request):
    incident_id = request.data.get('incident_id')
    audit_finding_id = request.data.get('audit_finding_id')
    
    if incident_id:
        try:
            incident = Incident.objects.get(pk=incident_id)
            incident.Status = "Rejected"
            incident.save()
            return Response({'message': 'Incident rejected successfully.'}, status=status.HTTP_200_OK)
        except Incident.DoesNotExist:
            return Response({'error': 'Incident not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    elif audit_finding_id:
        try:
            finding = AuditFinding.objects.get(pk=audit_finding_id)
            
            # Check if an incident already exists for this finding
            existing_incident = Incident.objects.filter(
                Origin="Audit Finding",
                AuditId=finding.AuditId,
                ComplianceId=finding.ComplianceId
            ).first()
            
            if existing_incident:
                existing_incident.Status = "Rejected"
                existing_incident.save()
            else:
                # Create a new incident with Rejected status
                incident_data = {
                    'IncidentTitle': finding.ComplianceId.ComplianceItemDescription if finding.ComplianceId else "Audit Finding",
                    'Description': finding.DetailsOfFinding or finding.Comments or "",
                    'Mitigation': finding.ComplianceId.mitigation if finding.ComplianceId else "",
                    'AuditId': finding.AuditId.pk if finding.AuditId else None,
                    'ComplianceId': finding.ComplianceId.pk if finding.ComplianceId else None,
                    'Date': finding.AssignedDate.date() if finding.AssignedDate else None,
                    'Time': finding.AssignedDate.time() if finding.AssignedDate else None,
                    'UserId': finding.UserId.UserId,
                    'Origin': 'Audit Finding',
                    'Comments': finding.Comments,
                    'Status': 'Rejected',
                }
                
                serializer = IncidentSerializer(data=incident_data)
                if serializer.is_valid():
                    serializer.save()
                    # Mark finding as processed
                    finding.Check = '1'
                    finding.save()
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
            return Response({'message': 'Audit finding rejected successfully.'}, status=status.HTTP_200_OK)
            
        except AuditFinding.DoesNotExist:
            return Response({'error': 'Audit finding not found.'}, status=status.HTTP_404_NOT_FOUND)
    
    else:
        return Response({'error': 'No incident_id or audit_finding_id provided.'}, status=status.HTTP_400_BAD_REQUEST)


"""
@api POST /api/frameworks/{framework_id}/policies/
Adds a new policy to an existing framework.
New policies are created with Status='Under Review' and ActiveInactive='Inactive' by default.
CurrentVersion defaults to 1.0 if not provided.
 
Example payload:
{
  "PolicyName": "Data Classification Policy",
  "PolicyDescription": "Guidelines for data classification and handling",
  "StartDate": "2023-10-01",
  "Department": "IT,Legal",
  "Applicability": "All Employees",
  "Scope": "All company data",
  "Objective": "Ensure proper data classification and handling",
  "Identifier": "DCP-001",
  "subpolicies": [
    {
      "SubPolicyName": "Confidential Data Handling",
      "Identifier": "CDH-001",
      "Description": "Guidelines for handling confidential data",
      "PermanentTemporary": "Permanent",
      "Control": "Encrypt all confidential data at rest and in transit"
    }
  ]
}
"""
@api_view(['POST'])
@permission_classes([AllowAny])
def add_policy_to_framework(request, framework_id):
    framework = get_object_or_404(Framework, FrameworkId=framework_id)
    try:
        with transaction.atomic():
            policy_data = request.data.copy()
            policy_data['FrameworkId'] = framework.FrameworkId
            policy_data['CurrentVersion'] = framework.CurrentVersion
            if 'Status' not in policy_data:
                policy_data['Status'] = 'Under Review'
            if 'ActiveInactive' not in policy_data:
                policy_data['ActiveInactive'] = 'Inactive'
            if 'CreatedByName' not in policy_data:
                policy_data['CreatedByName'] = framework.CreatedByName
            if 'CreatedByDate' not in policy_data:
                policy_data['CreatedByDate'] = datetime.date.today()
           
            policy_serializer = PolicySerializer(data=policy_data)
            if not policy_serializer.is_valid():
                return Response(policy_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            policy = policy_serializer.save()

            # --- PolicyApproval logic ---
            reviewer_id = request.data.get('reviewer')

            # Get user id from CreatedByName
            created_by_name = policy_data.get('CreatedByName')
            user_obj = Users.objects.filter(UserName=created_by_name).first()
            user_id = user_obj.UserId if user_obj else None
            
            # Structure the ExtractedData to include approval fields
            extracted_data = request.data.copy()
            
            # Add policy approval structure
            extracted_data['policy_approval'] = {
                'approved': None,
                'remarks': ''
            }
            
            # Add subpolicy approval structure
            subpolicies_data = extracted_data.get('subpolicies', [])
            for i, subpolicy in enumerate(subpolicies_data):
                subpolicy['approval'] = {
                    'approved': None,
                    'remarks': ''
                }
            
            # Create policy approval with initial version "u1"
            PolicyApproval.objects.create(
                Identifier=policy.Identifier,
                ExtractedData=extracted_data,  # Save the structured data as JSON
                UserId=user_id,
                ReviewerId=reviewer_id,
                ApprovedNot=None,
                Version="u1"  # Initial user version
            )
            # --- end PolicyApproval logic ---
           
            # Create policy version record
            policy_version = PolicyVersion(
                PolicyId=policy,
                Version=policy.CurrentVersion,
                PolicyName=policy.PolicyName,
                CreatedBy=policy.CreatedByName,
                CreatedDate=policy.CreatedByDate,
                PreviousVersionId=None
            )
            policy_version.save()
           
            # Create subpolicies if provided
            for subpolicy_data in subpolicies_data:
                # Set policy ID and default values
                subpolicy_data = subpolicy_data.copy() if isinstance(subpolicy_data, dict) else {}
                subpolicy_data['PolicyId'] = policy.PolicyId
                if 'CreatedByName' not in subpolicy_data:
                    subpolicy_data['CreatedByName'] = policy.CreatedByName
                if 'CreatedByDate' not in subpolicy_data:
                    subpolicy_data['CreatedByDate'] = policy.CreatedByDate
                if 'Status' not in subpolicy_data:
                    subpolicy_data['Status'] = 'Under Review'
               
                subpolicy_serializer = SubPolicySerializer(data=subpolicy_data)
                if not subpolicy_serializer.is_valid():
                    return Response(subpolicy_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
               
                subpolicy_serializer.save()
           
            return Response({
                'message': 'Policy added to framework successfully',
                'PolicyId': policy.PolicyId,
                'FrameworkId': framework.FrameworkId,
                'Version': policy.CurrentVersion
            }, status=status.HTTP_201_CREATED)
    except Exception as e:
        error_info = {
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        return Response({'error': 'Error adding policy to framework', 'details': error_info}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_policy_approvals_for_reviewer(request):
    # For now, reviewer_id is hardcoded as 2
    reviewer_id = 2
    
    # Get the latest version of each policy by identifier
    unique_identifiers = PolicyApproval.objects.values('Identifier').distinct()
    latest_approvals = []
    
    for identifier_obj in unique_identifiers:
        identifier = identifier_obj['Identifier']
        # Find the latest approval record for this identifier
        latest = PolicyApproval.objects.filter(
            Identifier=identifier,
            ReviewerId=reviewer_id
        ).order_by('-ApprovalId').first()
        
        if latest:
            latest_approvals.append(latest)
    
    # Serialize the data
    data = [
        {
            "ApprovalId": a.ApprovalId,
            "Identifier": a.Identifier,
            "ExtractedData": a.ExtractedData,
            "UserId": a.UserId,
            "ReviewerId": a.ReviewerId,
            "ApprovedNot": a.ApprovedNot,
            "Version": a.Version
        }
        for a in latest_approvals
    ]
    
    return Response(data)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_policy_approval(request, approval_id):
    try:
        # Get the original approval
        approval = PolicyApproval.objects.get(ApprovalId=approval_id)
        
        # Create a new approval object instead of updating
        new_approval = PolicyApproval()
        new_approval.Identifier = approval.Identifier
        new_approval.ExtractedData = request.data.get('ExtractedData', approval.ExtractedData)
        new_approval.UserId = approval.UserId
        new_approval.ReviewerId = approval.ReviewerId
        new_approval.ApprovedNot = request.data.get('ApprovedNot', approval.ApprovedNot)
        
        # Determine version prefix based on who made the change
        # For reviewers (assuming ReviewerId is the one making changes in this endpoint)
        prefix = 'r'
        
        # Get the latest version with this prefix for this identifier
        latest_version = PolicyApproval.objects.filter(
            Identifier=approval.Identifier,
            Version__startswith=prefix
        ).order_by('-Version').first()
        
        if latest_version and latest_version.Version:
            # Extract number and increment
            try:
                version_num = int(latest_version.Version[1:])
                new_approval.Version = f"{prefix}{version_num + 1}"
            except ValueError:
                new_approval.Version = f"{prefix}1"
        else:
            new_approval.Version = f"{prefix}1"
        
        new_approval.save()
        
        return Response({
            'message': 'Policy approval updated successfully',
            'ApprovalId': new_approval.ApprovalId,
            'Version': new_approval.Version
        })
    except PolicyApproval.DoesNotExist:
        return Response({'error': 'Policy approval not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([AllowAny])
def resubmit_policy_approval(request, approval_id):
    try:
        # Get the original approval
        approval = PolicyApproval.objects.get(ApprovalId=approval_id)
        
        # Validate data
        extracted_data = request.data.get('ExtractedData')
        if not extracted_data:
            return Response({'error': 'ExtractedData is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Print debug info
        print(f"Resubmitting policy with ID: {approval_id}, Identifier: {approval.Identifier}")
        
        # Get all versions for this identifier with 'u' prefix
        all_versions = PolicyApproval.objects.filter(Identifier=approval.Identifier)
        
        # Find the highest 'u' version number
        highest_u_version = 0
        for pa in all_versions:
            if pa.Version and pa.Version.startswith('u') and len(pa.Version) > 1:
                try:
                    version_num = int(pa.Version[1:])
                    if version_num > highest_u_version:
                        highest_u_version = version_num
                except ValueError:
                    continue
        
        # Set the new version
        new_version = f"u{highest_u_version + 1}"
        print(f"Setting new version: {new_version}")
        
        # Create a new approval object manually
        new_approval = PolicyApproval(
            Identifier=approval.Identifier,
            ExtractedData=extracted_data,
            UserId=approval.UserId,
            ReviewerId=approval.ReviewerId,
            ApprovedNot=None,  # Reset approval status
            Version=new_version
        )
        
        # Reset subpolicy approvals
        if 'subpolicies' in extracted_data and isinstance(extracted_data['subpolicies'], list):
            for subpolicy in extracted_data['subpolicies']:
                if subpolicy.get('approval', {}).get('approved') == False:
                    subpolicy['approval'] = {
                        'approved': None,
                        'remarks': ''
                    }
        
        # Save the new record
        new_approval.save()
        print(f"Saved new approval with ID: {new_approval.ApprovalId}, Version: {new_approval.Version}")
        
        return Response({
            'message': 'Policy resubmitted for review successfully',
            'ApprovalId': new_approval.ApprovalId,
            'Version': new_version
        })
        
    except PolicyApproval.DoesNotExist:
        return Response({'error': 'Policy approval not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("Error in resubmit_policy_approval:", str(e))
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def list_rejected_policy_approvals_for_user(request, user_id):
    # Filter policies by ReviewerId (not UserId) since we want reviewer's view
    approvals = PolicyApproval.objects.filter(ReviewerId=user_id)
    
    # Group by Identifier to find the latest for each policy/compliance
    identifier_latest = {}
    for approval in approvals:
        identifier = approval.Identifier
        if identifier not in identifier_latest or approval.ApprovalId > identifier_latest[identifier].ApprovalId:
            identifier_latest[identifier] = approval
    
    result = []
    for identifier, approval in identifier_latest.items():
        extracted = approval.ExtractedData
        
        # Check if this is a compliance item
        is_compliance = extracted.get('type') == 'compliance'
        
        # Check if main policy/compliance is rejected
        main_rejected = approval.ApprovedNot is False
        
        if is_compliance:
            # For compliance items
            item_rejected = extracted.get('compliance_approval', {}).get('approved') is False
            
            if main_rejected or item_rejected:
                result.append({
                    "ApprovalId": approval.ApprovalId,
                    "Identifier": approval.Identifier,
                    "ExtractedData": approval.ExtractedData,
                    "UserId": approval.UserId,
                    "ReviewerId": approval.ReviewerId,
                    "ApprovedNot": approval.ApprovedNot,
                    "main_item_rejected": main_rejected,
                    "is_compliance": True,
                    "rejection_reason": extracted.get('compliance_approval', {}).get('remarks', "")
                })
        else:
            # For policy items (existing logic)
            main_policy_rejected = main_rejected or (
                extracted.get('policy_approval', {}).get('approved') is False
            )
            # Check for rejected subpolicies
            rejected_subpolicies = []
            for sub in extracted.get('subpolicies', []):
                if sub.get('approval', {}).get('approved') is False:
                    rejected_subpolicies.append({
                        "Identifier": sub.get("Identifier"),
                        "SubPolicyName": sub.get("SubPolicyName"),
                        "Description": sub.get("Description"),
                        "Control": sub.get("Control"),
                        "remarks": sub.get("approval", {}).get("remarks", "")
                    })
            # Only add if main policy or any subpolicy is rejected
            if main_policy_rejected or rejected_subpolicies:
                result.append({
                    "ApprovalId": approval.ApprovalId,
                    "Identifier": approval.Identifier,
                    "ExtractedData": approval.ExtractedData,
                    "UserId": approval.UserId,
                    "ReviewerId": approval.ReviewerId,
                    "ApprovedNot": approval.ApprovedNot,
                    "main_policy_rejected": main_policy_rejected,
                    "rejected_subpolicies": rejected_subpolicies,
                    "is_compliance": False
                })
    return Response(result)

@api_view(['PUT'])
@permission_classes([AllowAny])
def submit_policy_review(request, approval_id):
    try:
        # Get the original approval
        approval = PolicyApproval.objects.get(ApprovalId=approval_id)
        
        # Validate and prepare data
        extracted_data = request.data.get('ExtractedData')
        if not extracted_data:
            return Response({'error': 'ExtractedData is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        approved_not = request.data.get('ApprovedNot')
        
        # Simply create a new PolicyApproval object
        # Avoid using filters that might generate BINARY expressions
        new_version = "r1"  # Default version for reviewer
        
        # Try to determine the next version number without SQL LIKE
        try:
            r_versions = []
            for pa in PolicyApproval.objects.filter(Identifier=approval.Identifier):
                if pa.Version and pa.Version.startswith('r') and pa.Version[1:].isdigit():
                    r_versions.append(int(pa.Version[1:]))
            
            if r_versions:
                new_version = f"r{max(r_versions) + 1}"
        except Exception as version_err:
            print(f"Error determining version (using default): {str(version_err)}")
            
        # Create a new record using Django ORM
        new_approval = PolicyApproval(
            Identifier=approval.Identifier,
            ExtractedData=extracted_data,
            UserId=approval.UserId,
            ReviewerId=approval.ReviewerId,
            ApprovedNot=approved_not,
            Version=new_version
        )
        new_approval.save()
        
        # If policy is approved (ApprovedNot=1), update the status in policy and subpolicies tables
        if approved_not == True or approved_not == 1:
            try:
                # Find the policy by Identifier
                policy = Policy.objects.get(Identifier=approval.Identifier)
                
                # Update policy status to Approved
                if policy.Status == 'Under Review':
                    policy.Status = 'Approved'
                    policy.save()
                    print(f"Updated policy {policy.Identifier} status to Approved")
                
                # Update all subpolicies for this policy
                subpolicies = SubPolicy.objects.filter(PolicyId=policy.PolicyId)
                for subpolicy in subpolicies:
                    if subpolicy.Status == 'Under Review':
                        subpolicy.Status = 'Approved'
                        subpolicy.save()
                        print(f"Updated subpolicy {subpolicy.Identifier} status to Approved")
            except Exception as update_error:
                print(f"Error updating policy/subpolicy status: {str(update_error)}")
                # Continue with the response even if status update fails
        
        return Response({
            'message': 'Policy review submitted successfully',
            'ApprovalId': new_approval.ApprovalId,
            'Version': new_approval.Version
        })
        
    except PolicyApproval.DoesNotExist:
        return Response({'error': 'Policy approval not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("Error in submit_policy_review:", str(e))
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_frameworks(request):
    frameworks = Framework.objects.filter(ActiveInactive='Active')
    serializer = FrameworkSerializer(frameworks, many=True)
    return Response({'success': True, 'data': serializer.data})

@api_view(['GET'])
def get_subpolicies(request, policy_id):
    # Change Policy_id to PolicyId to match your model definition
    subpolicies = SubPolicy.objects.filter(PolicyId=policy_id, Status='Active')
    serializer = SubPolicySerializer(subpolicies, many=True)
    return Response({'success': True, 'data': serializer.data})

@api_view(['POST'])
def create_compliance(request):
    request_data = request.data.copy()
    
    # Set defaults
    if 'Status' not in request_data:
        request_data['Status'] = 'Under Review'
    
    if 'ActiveInactive' not in request_data:
        request_data['ActiveInactive'] = 'Active'
    
    if 'mitigation' not in request_data:
        request_data['mitigation'] = ""
    
    # Generate Identifier if not provided (optional)
    if 'Identifier' not in request_data:
        subpolicy_id = request_data.get('SubPolicyId')
        if subpolicy_id:
            request_data['Identifier'] = f"COMP-{subpolicy_id}-{datetime.date.today().strftime('%y%m%d')}"
        else:
            request_data['Identifier'] = f"COMP-{datetime.date.today().strftime('%y%m%d')}-{uuid.uuid4().hex[:6]}"
    
    serializer = ComplianceCreateSerializer(data=request_data)
    if serializer.is_valid():
        # Get creator information
        created_by_name = request_data.get('CreatedByName', 'System')
        
        # Create the compliance object with CreateBy details
        compliance = serializer.save(
            CreatedByName=created_by_name,
            CreatedByDate=datetime.date.today()
        )
        
        # --- PolicyApproval logic for compliance ---
        # Get reviewer ID from request data
        reviewer_id = int(request_data.get('reviewer', 2))  # Default to 2 if not provided
        
        # Look up the user ID based on CreatedByName
        try:
            # Query the Users table to find the user with matching UserName
            user = Users.objects.get(UserName=created_by_name)
            user_id = user.UserId
            print(f"Found user ID {user_id} for user {created_by_name}")
        except Users.DoesNotExist:
            # If user not found, default to 1
            user_id = 1
            print(f"User {created_by_name} not found in Users table, defaulting to user_id=1")
        except Exception as e:
            # Handle any other exceptions
            user_id = 1
            print(f"Error finding user {created_by_name}: {str(e)}")
        
        # Print debug information
        print(f"Creating compliance approval with UserId: {user_id}, ReviewerId: {reviewer_id}")
        
        # Structure the ExtractedData to include approval fields
        extracted_data = request_data.copy()
        extracted_data['type'] = 'compliance'  # Mark as compliance for frontend differentiation
        
        # Add compliance approval structure
        extracted_data['compliance_approval'] = {
            'approved': None,
            'remarks': ''
        }
        
        # Create policy approval with initial version "u1" - explicitly set the fields
        PolicyApproval.objects.create(
            Identifier=compliance.Identifier,
            ExtractedData=extracted_data,
            UserId=user_id,
            ReviewerId=reviewer_id,
            ApprovedNot=None,
            Version="u1"  # Initial user version
        )
        
        return Response({
            'success': True,
            'message': 'Compliance created successfully',
            'compliance_id': compliance.ComplianceId,
            'identifier': compliance.Identifier,
            'version': compliance.ComplianceVersion
        }, status=201)
    
    return Response({'success': False, 'errors': serializer.errors}, status=400)

@api_view(['PUT'])
def edit_compliance(request, compliance_id):
    try:
        compliance = get_object_or_404(Compliance, ComplianceId=compliance_id)
        serializer = ComplianceCreateSerializer(compliance, data=request.data, partial=True)
        
        if serializer.is_valid():
            # Get user information
            user_id = request.session.get('UserId', 7)
            try:
                user = Users.objects.get(UserId=user_id)
                authorized_by_name = user.UserName
            except Users.DoesNotExist:
                authorized_by_name = "System"
            
            # Update authorized by information
            compliance_data = serializer.validated_data
            # compliance_data['AuthorizedByName'] = authorized_by_name
            # compliance_data['AuthorizedByDate'] = datetime.date.today()
            
            # Save the updated compliance
            serializer.save()
            
            return Response({
                'success': True,
                'message': 'Compliance updated successfully',
                'compliance_id': compliance.ComplianceId
            })
        return Response({
            'success': False,
            'errors': serializer.errors
        }, status=status.HTTP_400_BAD_REQUEST)
        
    except Compliance.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Compliance not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
def clone_compliance(request, compliance_id):
    try:
        # Get the source compliance
        source_compliance = get_object_or_404(Compliance, ComplianceId=compliance_id)
        
        # Get user information
        user_id = request.session.get('UserId', 7)
        try:
            user = Users.objects.get(UserId=user_id)
            created_by_name = user.UserName
        except Users.DoesNotExist:
            created_by_name = "System"

        # Get the target subpolicy from request data (optional)
        target_subpolicy_id = request.data.get('target_subpolicy_id')
        
        if target_subpolicy_id:
            # Clone to a different subpolicy
            try:
                target_subpolicy = SubPolicy.objects.get(SubPolicyId=target_subpolicy_id)
            except SubPolicy.DoesNotExist:
                return Response({
                    'success': False,
                    'message': 'Target subpolicy not found'
                }, status=status.HTTP_404_NOT_FOUND)
            
            # Start with version 1.0 for new subpolicy
            new_version = "1.0"
        else:
            # Clone to same subpolicy
            target_subpolicy = source_compliance.SubPolicy
            # Increment version by 1
            try:
                current_version = float(source_compliance.ComplianceVersion)
                new_version = f"{current_version + 1.0:.1f}"
            except ValueError:
                new_version = "1.0"

        # Create new compliance data
        compliance_data = {
            'SubPolicy': target_subpolicy,
            'ComplianceItemDescription': request.data.get('ComplianceItemDescription', source_compliance.ComplianceItemDescription),
            'IsRisk': request.data.get('IsRisk', source_compliance.IsRisk),
            'PossibleDamage': request.data.get('PossibleDamage', source_compliance.PossibleDamage),
            'mitigation': request.data.get('mitigation', source_compliance.mitigation),
            'Criticality': request.data.get('Criticality', source_compliance.Criticality),
            'MandatoryOptional': request.data.get('MandatoryOptional', source_compliance.MandatoryOptional),
            'ManualAutomatic': request.data.get('ManualAutomatic', source_compliance.ManualAutomatic),
            'Impact': request.data.get('Impact', source_compliance.Impact),
            'Probability': request.data.get('Probability', source_compliance.Probability),
            'ActiveInactive': request.data.get('ActiveInactive', source_compliance.ActiveInactive),
            'PermanentTemporary': request.data.get('PermanentTemporary', source_compliance.PermanentTemporary),
            'Status': request.data.get('Status', 'Under Review'),
            'ComplianceVersion': new_version,
            'CreatedByName': created_by_name,
            'CreatedByDate': datetime.date.today()
        }

        # Create new compliance
        new_compliance = Compliance.objects.create(**compliance_data)

        return Response({
            'success': True,
            'message': 'Compliance cloned successfully',
            'compliance_id': new_compliance.ComplianceId,
            'version': new_version
        }, status=status.HTTP_201_CREATED)

    except Compliance.DoesNotExist:
        return Response({
            'success': False,
            'message': 'Source compliance not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_compliance_dashboard(request):
    try:
        # Get all filter parameters from request
        status = request.query_params.get('status')
        active_inactive = request.query_params.get('active_inactive')
        criticality = request.query_params.get('criticality')
        mandatory_optional = request.query_params.get('mandatory_optional')
        manual_automatic = request.query_params.get('manual_automatic')
        impact = request.query_params.get('impact')
        probability = request.query_params.get('probability')
        permanent_temporary = request.query_params.get('permanent_temporary')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        framework_id = request.query_params.get('framework_id')
        policy_id = request.query_params.get('policy_id')
        subpolicy_id = request.query_params.get('subpolicy_id')

        # Start with base queryset
        queryset = Compliance.objects.all()

        # Apply filters if they exist
        if status:
            queryset = queryset.filter(Status=status)
        if active_inactive:
            queryset = queryset.filter(ActiveInactive=active_inactive)
        if criticality:
            queryset = queryset.filter(Criticality=criticality)
        if mandatory_optional:
            queryset = queryset.filter(MandatoryOptional=mandatory_optional)
        if manual_automatic:
            queryset = queryset.filter(ManualAutomatic=manual_automatic)
        if impact:
            queryset = queryset.filter(Impact=impact)
        if probability:
            queryset = queryset.filter(Probability=probability)
        if permanent_temporary:
            queryset = queryset.filter(PermanentTemporary=permanent_temporary)
        if start_date:
            queryset = queryset.filter(CreatedByDate__gte=start_date)
        if end_date:
            queryset = queryset.filter(CreatedByDate__lte=end_date)
        if subpolicy_id:
            queryset = queryset.filter(SubPolicy_id=subpolicy_id)
        elif policy_id:
            queryset = queryset.filter(SubPolicy__Policy_id=policy_id)
        elif framework_id:
            queryset = queryset.filter(SubPolicy_Policy_Framework_id=framework_id)

        # Serialize the filtered data
        serializer = ComplianceCreateSerializer(queryset, many=True)
        
        # Get counts for different statuses
        status_counts = {
            'approved': queryset.filter(Status='Approved').count(),
            'active': queryset.filter(Status='Active').count(),
            'scheduled': queryset.filter(Status='Schedule').count(),
            'rejected': queryset.filter(Status='Rejected').count(),
            'under_review': queryset.filter(Status='Under Review').count()
        }

        # Get counts for criticality levels
        criticality_counts = {
            'high': queryset.filter(Criticality='High').count(),
            'medium': queryset.filter(Criticality='Medium').count(),
            'low': queryset.filter(Criticality='Low').count()
        }

        return Response({
            'success': True,
            'data': {
                'compliances': serializer.data,
                'summary': {
                    'status_counts': status_counts,
                    'criticality_counts': criticality_counts,
                    'total_count': queryset.count()
                }
            }
        })

    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def submit_compliance_review(request, approval_id):
    try:
        # Get the original approval
        approval = PolicyApproval.objects.get(ApprovalId=approval_id)
        
        # Validate and prepare data
        extracted_data = request.data.get('ExtractedData')
        if not extracted_data:
            return Response({'error': 'ExtractedData is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        approved_not = request.data.get('ApprovedNot')
        
        # Print received data for debugging
        print(f"Received review data - ApprovedNot: {approved_not}")
        print(f"compliance_approval: {extracted_data.get('compliance_approval')}")
        
        # Create new version
        new_version = "r1"  # Default version for reviewer
        
        # Try to determine the next version number
        try:
            r_versions = []
            for pa in PolicyApproval.objects.filter(Identifier=approval.Identifier):
                if pa.Version and pa.Version.startswith('r') and pa.Version[1:].isdigit():
                    r_versions.append(int(pa.Version[1:]))
            
            if r_versions:
                new_version = f"r{max(r_versions) + 1}"
        except Exception as version_err:
            print(f"Error determining version (using default): {str(version_err)}")
            
        # Create a new record using Django ORM
        new_approval = PolicyApproval(
            Identifier=approval.Identifier,
            ExtractedData=extracted_data,
            UserId=approval.UserId,
            ReviewerId=approval.ReviewerId,
            ApprovedNot=approved_not,
            Version=new_version
        )
        new_approval.save()
        print(f"Saved new approval with ID: {new_approval.ApprovalId}, Version: {new_version}")
        
        # If compliance is approved/rejected, update status in Compliance table
        status_to_set = None
        if approved_not is True:
            status_to_set = 'Approved'
        elif approved_not is False:
            status_to_set = 'Rejected'
            
        if status_to_set:
            try:
                # Find the compliance by Identifier
                compliance = Compliance.objects.get(Identifier=approval.Identifier)
                
                # Update compliance status
                if compliance.Status == 'Under Review':
                    compliance.Status = status_to_set
                    compliance.save()
                    print(f"Updated compliance {compliance.Identifier} status to {status_to_set}")
                
            except Exception as update_error:
                print(f"Error updating compliance status: {str(update_error)}")
        
        return Response({
            'message': 'Compliance review submitted successfully',
            'ApprovalId': new_approval.ApprovalId,
            'Version': new_approval.Version
        })
        
    except PolicyApproval.DoesNotExist:
        return Response({'error': 'Policy approval not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("Error in submit_compliance_review:", str(e))
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([AllowAny])
def resubmit_compliance_approval(request, approval_id):
    try:
        # Get the original approval
        approval = PolicyApproval.objects.get(ApprovalId=approval_id)
        
        # Validate data
        extracted_data = request.data.get('ExtractedData')
        if not extracted_data:
            return Response({'error': 'ExtractedData is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        print(f"Resubmitting compliance with ID: {approval_id}, Identifier: {approval.Identifier}")
        
        # Get all versions for this identifier with 'u' prefix
        all_versions = PolicyApproval.objects.filter(Identifier=approval.Identifier)
        
        # Find the highest 'u' version number
        highest_u_version = 0
        for pa in all_versions:
            if pa.Version and pa.Version.startswith('u') and len(pa.Version) > 1:
                try:
                    version_num = int(pa.Version[1:])
                    if version_num > highest_u_version:
                        highest_u_version = version_num
                except ValueError:
                    continue
        
        # Set the new version
        new_version = f"u{highest_u_version + 1}"
        print(f"Setting new version: {new_version}")
        
        # Reset approval status in the ExtractedData
        if 'compliance_approval' in extracted_data:
            extracted_data['compliance_approval']['approved'] = None
            extracted_data['compliance_approval']['remarks'] = ''
        
        # Create a new approval object
        new_approval = PolicyApproval(
            Identifier=approval.Identifier,
            ExtractedData=extracted_data,
            UserId=approval.UserId,
            ReviewerId=approval.ReviewerId,
            ApprovedNot=None,  # Reset approval status
            Version=new_version
        )
        
        # Save the new record
        new_approval.save()
        print(f"Saved new approval with ID: {new_approval.ApprovalId}, Version: {new_approval.Version}")
        
        return Response({
            'message': 'Compliance resubmitted for review successfully',
            'ApprovalId': new_approval.ApprovalId,
            'Version': new_version
        })
        
    except PolicyApproval.DoesNotExist:
        return Response({'error': 'Policy approval not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print("Error in resubmit_compliance_approval:", str(e))
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)