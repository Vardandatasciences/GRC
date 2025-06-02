from django.shortcuts import render, get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from .models import *
from .serializers import *
from django.utils import timezone   
import datetime
import uuid
from django.db import models
from django.views.decorators.csrf import csrf_exempt
from django.http import HttpResponse
from .export_service import export_data as export_service
from django.db.models import Prefetch
from django.http import JsonResponse
import json
import pandas as pd
from io import BytesIO

 
# Create your views here.
 
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
def test_connection(request):
    return Response({"message": "Connection successful!"})
 
@api_view(['GET'])
def get_frameworks(request):
    frameworks = Framework.objects.filter(ActiveInactive='Active')
    serializer = FrameworkSerializer(frameworks, many=True)
    return Response({'success': True, 'data': serializer.data})
 
@api_view(['GET'])
def get_policies(request, framework_id):
    policies = Policy.objects.filter(Framework_id=framework_id, ActiveInactive='Active')
    serializer = PolicySerializer(policies, many=True)
    return Response({'success': True, 'data': serializer.data})
 
@api_view(['GET'])
def get_subpolicies(request, policy_id):
    subpolicies = SubPolicy.objects.filter(Policy_id=policy_id, Status='Active')
    serializer = SubPolicySerializer(subpolicies, many=True)
    return Response({'success': True, 'data': serializer.data})
 
@api_view(['POST'])
def create_compliance(request):
    request_data = request.data.copy()
   
    # Set defaults
    request_data['Status'] = 'Under Review'  # Always set to "Under Review"
   
    if 'ActiveInactive' not in request_data:
        request_data['ActiveInactive'] = 'Inactive'
   
    if 'PermanentTemporary' not in request_data:
        request_data['PermanentTemporary'] = 'Permanent'
   
    if 'mitigation' not in request_data:
        request_data['mitigation'] = ""
       
    if 'MaturityLevel' not in request_data:
        request_data['MaturityLevel'] = 'Initial'
   
    # Allow manual Identifier or generate one
    if not request_data.get('Identifier'):
        subpolicy_id = request_data.get('SubPolicy')
        identifier = f"COMP-{subpolicy_id}-{datetime.date.today().strftime('%y%m%d')}-{uuid.uuid4().hex[:6]}"
        request_data['Identifier'] = identifier
    else:
        identifier = request_data.get('Identifier')
   
    # Get reviewer ID from request data
    reviewer_id = request_data.get('reviewer', 2)  # Default to 2 if not provided
   
    # Get creator name - from session or default
    created_by_name = request_data.get('CreatedByName', 'System')
    if request.user.is_authenticated:
        created_by_name = request.user.username
   
    serializer = ComplianceCreateSerializer(data=request_data)
    if serializer.is_valid():
        # Create compliance with explicit identifier field
        compliance = Compliance.objects.create(
            SubPolicy_id=request_data.get('SubPolicy'),
            ComplianceItemDescription=request_data.get('ComplianceItemDescription', ''),
            IsRisk=request_data.get('IsRisk', False),
            PossibleDamage=request_data.get('PossibleDamage', ''),
            mitigation=request_data.get('mitigation', ''),
            Criticality=request_data.get('Criticality', 'Medium'),
            MandatoryOptional=request_data.get('MandatoryOptional', 'Mandatory'),
            ManualAutomatic=request_data.get('ManualAutomatic', 'Manual'),
            Impact=request_data.get('Impact', 5.0),
            Probability=request_data.get('Probability', 5.0),
            MaturityLevel=request_data.get('MaturityLevel', 'Initial'),
            ActiveInactive=request_data.get('ActiveInactive', 'Inactive'),
            PermanentTemporary=request_data.get('PermanentTemporary', 'Permanent'),
            Status='Under Review',  # Always set to "Under Review"
            ComplianceVersion=request_data.get('ComplianceVersion', '1.0'),
            CreatedByName=created_by_name,
            CreatedByDate=datetime.date.today(),
            Identifier=identifier  # Set identifier explicitly
        )
       
        # Structure the ExtractedData to include approval fields
        extracted_data = request_data.copy()
        extracted_data['type'] = 'compliance'  # Mark as compliance for frontend differentiation
        extracted_data['Identifier'] = identifier  # Add identifier to extracted data
       
        # Add compliance approval structure
        extracted_data['compliance_approval'] = {
            'approved': None,
            'remarks': ''
        }
       
        # Create policy approval with initial version "u1" - explicitly set the fields
        # First make sure the user exists
        user_id = 1  # Default user ID
       
        # Check if reviewer exists in users table
        try:
            # Make sure the user exists in the database
            from .models import User
            # Create the user if not exists
            if not User.objects.filter(UserId=user_id).exists():
                User.objects.create(UserId=user_id, UserName="System", Password="")
               
            # Create the reviewer if not exists
            if not User.objects.filter(UserId=reviewer_id).exists():
                User.objects.create(UserId=reviewer_id, UserName=f"Reviewer{reviewer_id}", Password="")
           
            PolicyApproval.objects.create(
                Identifier=identifier,
                ExtractedData=extracted_data,
                UserId=user_id,
                ReviewerId=reviewer_id,
                ApprovedNot=None,
                Version="u1"  # Initial user version
            )
        except Exception as e:
            print(f"Error creating PolicyApproval: {str(e)}")
            # Continue even if policy approval creation fails
       
        return Response({
            'success': True,
            'message': 'Compliance created successfully',
            'compliance_id': compliance.ComplianceId,
            'Identifier': identifier,
            'version': compliance.ComplianceVersion
        }, status=201)
   
    return Response({'success': False, 'errors': serializer.errors}, status=400)
 
@api_view(['PUT'])
def edit_compliance(request, compliance_id):
    try:
        # Get the original compliance
        original_compliance = get_object_or_404(Compliance, ComplianceId=compliance_id)
       
        # Make a copy of request data
        data = request.data.copy()
       
        # Get reviewer ID from request data or use default
        reviewer_id = data.get('reviewer_id', 2)  # Default to reviewer ID 2 if not provided
       
        # Validate reviewer exists
        try:
            reviewer = User.objects.get(UserId=reviewer_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': f'Reviewer with ID {reviewer_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
       
        # Get the SubPolicy instance
        subpolicy_id = data.get('SubPolicy', original_compliance.SubPolicy_id)
        try:
            subpolicy = SubPolicy.objects.get(SubPolicyId=subpolicy_id)
        except SubPolicy.DoesNotExist:
            return Response({
                'success': False,
                'message': f'SubPolicy with id {subpolicy_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
       
        # Create new compliance data
        new_compliance_data = {
            'SubPolicy': subpolicy,
            'ComplianceItemDescription': data.get('ComplianceItemDescription', original_compliance.ComplianceItemDescription),
            'IsRisk': data.get('IsRisk', original_compliance.IsRisk),
            'PossibleDamage': data.get('PossibleDamage', original_compliance.PossibleDamage),
            'mitigation': data.get('mitigation', original_compliance.mitigation),
            'Criticality': data.get('Criticality', original_compliance.Criticality),
            'MandatoryOptional': data.get('MandatoryOptional', original_compliance.MandatoryOptional),
            'ManualAutomatic': data.get('ManualAutomatic', original_compliance.ManualAutomatic),
            'Impact': data.get('Impact', original_compliance.Impact),
            'Probability': data.get('Probability', original_compliance.Probability),
            'MaturityLevel': data.get('MaturityLevel', original_compliance.MaturityLevel or 'Initial'),
            'ActiveInactive': 'Inactive',  # Always Inactive for new version
            'PermanentTemporary': data.get('PermanentTemporary', original_compliance.PermanentTemporary),
            'Status': 'Under Review',  # Always Under Review for new version
            'Identifier': data.get('Identifier', original_compliance.Identifier),
            'PreviousComplianceVersionId': original_compliance,
            'CreatedByName': request.data.get('CreatedByName', 'System'),
            'CreatedByDate': timezone.now().date()
        }
       
        # Handle version increment
        if 'ComplianceVersion' in data:
            new_compliance_data['ComplianceVersion'] = data['ComplianceVersion']
        else:
            current_version = float(original_compliance.ComplianceVersion) if original_compliance.ComplianceVersion else 1.0
            new_compliance_data['ComplianceVersion'] = str(int(current_version) + 1) + '.0'
       
        # Create new compliance using Django ORM
        new_compliance = Compliance.objects.create(**new_compliance_data)
 
        # Create policy approval record for the edited compliance
        extracted_data = {
            'type': 'compliance',
            'Identifier': new_compliance.Identifier,
            'SubPolicy': subpolicy_id,
            'ComplianceItemDescription': new_compliance.ComplianceItemDescription,
            'IsRisk': new_compliance.IsRisk,
            'PossibleDamage': new_compliance.PossibleDamage,
            'mitigation': new_compliance.mitigation,
            'Criticality': new_compliance.Criticality,
            'MandatoryOptional': new_compliance.MandatoryOptional,
            'ManualAutomatic': new_compliance.ManualAutomatic,
            'Impact': new_compliance.Impact,
            'Probability': new_compliance.Probability,
            'MaturityLevel': new_compliance.MaturityLevel,
            'ActiveInactive': new_compliance.ActiveInactive,
            'PermanentTemporary': new_compliance.PermanentTemporary,
            'Status': new_compliance.Status,
            'ComplianceVersion': new_compliance.ComplianceVersion,
            'CreatedByName': new_compliance.CreatedByName,
            'CreatedByDate': new_compliance.CreatedByDate.isoformat() if new_compliance.CreatedByDate else None,
            'compliance_approval': {
                'approved': None,
                'remarks': ''
            }
        }
 
        # Create policy approval record with initial version "u1"
        try:
            PolicyApproval.objects.create(
                Identifier=new_compliance.Identifier,
                ExtractedData=extracted_data,
                UserId=1,  # System user
                ReviewerId=reviewer_id,
                ApprovedNot=None,
                Version="u1"  # Initial user version
            )
        except Exception as e:
            print(f"Error creating policy approval: {str(e)}")
            # Continue even if policy approval creation fails
           
        return Response({
            'success': True,
            'message': 'New compliance version created successfully and sent for review',
            'compliance_id': new_compliance.ComplianceId,
            'previous_compliance_id': original_compliance.ComplianceId,
            'version': new_compliance.ComplianceVersion,
            'reviewer_id': reviewer_id
        })
       
    except Exception as e:
        print(f"Error in edit_compliance: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['POST'])
def clone_compliance(request, compliance_id):
    try:
        # Get the source compliance
        source_compliance = get_object_or_404(Compliance, ComplianceId=compliance_id)
       
        # Get the target subpolicy from request data
        target_subpolicy_id = request.data.get('target_subpolicy_id')
       
        if not target_subpolicy_id:
            return Response({
                'success': False,
                'message': 'Target subpolicy ID is required'
            }, status=status.HTTP_400_BAD_REQUEST)
 
        # Validate that target subpolicy is different from source
        if target_subpolicy_id == source_compliance.SubPolicy_id:
            return Response({
                'success': False,
                'message': 'Cannot copy compliance to the same subpolicy'
            }, status=status.HTTP_400_BAD_REQUEST)
           
        try:
            target_subpolicy = SubPolicy.objects.get(SubPolicyId=target_subpolicy_id)
        except SubPolicy.DoesNotExist:
            return Response({
                'success': False,
                'message': 'Target subpolicy not found'
            }, status=status.HTTP_404_NOT_FOUND)

        # Get reviewer ID from request data or use default
        reviewer_id = request.data.get('reviewer_id', 2)  # Default to reviewer ID 2 if not provided
        
        # Validate reviewer exists
        try:
            reviewer = User.objects.get(UserId=reviewer_id)
        except User.DoesNotExist:
            return Response({
                'success': False,
                'message': f'Reviewer with ID {reviewer_id} not found'
            }, status=status.HTTP_404_NOT_FOUND)
 
        # Generate a new identifier for the cloned compliance
        identifier = f"COMP-{target_subpolicy_id}-{datetime.date.today().strftime('%y%m%d')}-{uuid.uuid4().hex[:6]}"
 
        # Create new compliance data with edited values from request
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
            'MaturityLevel': request.data.get('MaturityLevel', source_compliance.MaturityLevel or 'Initial'),
            'ActiveInactive': 'Inactive',  # Always Inactive for new version
            'PermanentTemporary': request.data.get('PermanentTemporary', source_compliance.PermanentTemporary),
            'Status': 'Under Review',  # Always Under Review for new version
            'ComplianceVersion': "1.0",  # Start with version 1.0 for new subpolicy
            'CreatedByName': request.data.get('CreatedByName', 'System'),
            'CreatedByDate': timezone.now().date(),
            'Identifier': identifier  # Set the identifier
        }
 
        # Create new compliance
        new_compliance = Compliance.objects.create(**compliance_data)
 
        # Create a policy approval record for the new compliance with the identifier
        extracted_data = {
            'type': 'compliance',
            'Identifier': identifier,
            'SubPolicy': target_subpolicy_id,
            'ComplianceItemDescription': new_compliance.ComplianceItemDescription,
            'IsRisk': new_compliance.IsRisk,
            'PossibleDamage': new_compliance.PossibleDamage,
            'mitigation': new_compliance.mitigation,
            'Criticality': new_compliance.Criticality,
            'MandatoryOptional': new_compliance.MandatoryOptional,
            'ManualAutomatic': new_compliance.ManualAutomatic,
            'Impact': new_compliance.Impact,
            'Probability': new_compliance.Probability,
            'MaturityLevel': new_compliance.MaturityLevel,
            'ActiveInactive': new_compliance.ActiveInactive,
            'PermanentTemporary': new_compliance.PermanentTemporary,
            'Status': new_compliance.Status,
            'ComplianceVersion': new_compliance.ComplianceVersion,
            'CreatedByName': new_compliance.CreatedByName,
            'CreatedByDate': new_compliance.CreatedByDate.isoformat() if new_compliance.CreatedByDate else None,
            'compliance_approval': {
                'approved': None,
                'remarks': ''
            }
        }
       
        # Create policy approval with initial version "u1"
        PolicyApproval.objects.create(
            Identifier=identifier,
            ExtractedData=extracted_data,
            UserId=1,  # System user
            ReviewerId=reviewer_id,
            ApprovedNot=None,
            Version="u1"  # Initial user version
        )
 
        return Response({
            'success': True,
            'message': 'Compliance cloned successfully and sent for review',
            'compliance_id': new_compliance.ComplianceId,
            'Identifier': identifier,
            'version': new_compliance.ComplianceVersion,
            'reviewer_id': reviewer_id
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


        
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from .models import Framework, Policy, SubPolicy, FrameworkVersion, PolicyVersion, PolicyApproval, Users
from .serializers import FrameworkSerializer, PolicySerializer, SubPolicySerializer, PolicyApprovalSerializer, UserSerializer   
from django.db import transaction
import traceback
import sys
import datetime
import re
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Avg, Case, When, Value, FloatField, F
from django.db.models.functions import Coalesce, Cast

# Framework CRUD operations

"""
@api GET /api/frameworks/
Returns all frameworks with Status='Approved' and ActiveInactive='Active'.
Filtered by the serializer to include only policies with Status='Approved' and ActiveInactive='Active',
and subpolicies with Status='Approved'.

@api POST /api/frameworks/
Creates a new framework with associated policies and subpolicies.
New frameworks are created with Status='Under Review' and ActiveInactive='Inactive' by default.
CurrentVersion defaults to 1.0 if not provided.

Example payload:
{
  "FrameworkName": "ISO 27001",
  "FrameworkDescription": "Information Security Management System",
  "EffectiveDate": "2023-10-01",
  "CreatedByName": "John Doe",
  "CreatedByDate": "2023-09-15",
  "Category": "Information Security and Compliance",
  "DocURL": "https://example.com/iso27001",
  "Identifier": "ISO-27001",
  "StartDate": "2023-10-01",
  "EndDate": "2025-10-01",
  "policies": [
    {
      "PolicyName": "Access Control Policy",
      "PolicyDescription": "Guidelines for access control management",
      "StartDate": "2023-10-01",
      "Department": "IT",
      "Applicability": "All Employees",
      "Scope": "All IT systems",
      "Objective": "Ensure proper access control",
      "Identifier": "ACP-001",
      "subpolicies": [
        {
          "SubPolicyName": "Password Management",
          "Identifier": "PWD-001",
          "Description": "Password requirements and management",
          "PermanentTemporary": "Permanent",
          "Control": "Use strong passwords with at least 12 characters"
        }
      ]
    }
  ]
}
"""
@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def framework_list(request):
    if request.method == 'GET':
        frameworks = Framework.objects.filter(Status='Approved', ActiveInactive='Active')
        serializer = FrameworkSerializer(frameworks, many=True)
        return Response(serializer.data)
 
    elif request.method == 'POST':
        try:
            with transaction.atomic():
                # Prepare incoming data
                data = request.data.copy()
 
                # Set default values if not provided
                data.setdefault('Status', 'Under Review')
                data.setdefault('ActiveInactive', 'Inactive')
               
                # Always set CreatedByDate to current date
                data['CreatedByDate'] = datetime.date.today()
 
                # Set version to 1.0 for all new frameworks
                new_version = 1.0
 
                # Create Framework
                framework_serializer = FrameworkSerializer(data=data)
                if not framework_serializer.is_valid():
                    return Response(framework_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
                framework = framework_serializer.save()
                framework.CurrentVersion = new_version
                framework.save()
 
                # Create FrameworkVersion
                framework_version = FrameworkVersion(
                    FrameworkId=framework,
                    Version=framework.CurrentVersion,
                    FrameworkName=framework.FrameworkName,
                    CreatedBy=framework.CreatedByName,
                    CreatedDate=datetime.date.today(),  # Always use current date
                    PreviousVersionId=None
                )
                framework_version.save()
 
                # Handle Policies if provided
                policies_data = request.data.get('policies', [])
                created_policies_count = 0
                created_subpolicies_count = 0
               
                for policy_data in policies_data:
                    policy_data = policy_data.copy()
                    policy_data['FrameworkId'] = framework.FrameworkId
                    policy_data['CurrentVersion'] = framework.CurrentVersion
                    policy_data.setdefault('Status', 'Under Review')
                    policy_data.setdefault('ActiveInactive', 'Inactive')
                    policy_data.setdefault('CreatedByName', framework.CreatedByName)
                    policy_data['CreatedByDate'] = datetime.date.today()  # Always use current date
                   
                    # Get reviewer's name if reviewer ID is provided
                    reviewer_id = policy_data.get('Reviewer')
                    if reviewer_id:
                        reviewer_obj = Users.objects.filter(UserId=reviewer_id).first()
                        if reviewer_obj:
                            # Store the reviewer's name in the policy
                            policy_data['Reviewer'] = reviewer_obj.UserName
 
                    policy_serializer = PolicySerializer(data=policy_data)
                    if not policy_serializer.is_valid():
                        return Response(policy_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
 
                    policy = policy_serializer.save()
                    created_policies_count += 1
 
                    policy_version = PolicyVersion(
                        PolicyId=policy,
                        Version=policy.CurrentVersion,
                        PolicyName=policy.PolicyName,
                        CreatedBy=policy.CreatedByName,
                        CreatedDate=datetime.date.today(),  # Always use current date
                        PreviousVersionId=None
                    )
                    policy_version.save()
                   
                    # Handle SubPolicies if provided
                    subpolicies_data = policy_data.get('subpolicies', [])
                    for subpolicy_data in subpolicies_data:
                        subpolicy_data = subpolicy_data.copy()
                        subpolicy_data['PolicyId'] = policy.PolicyId
                        subpolicy_data.setdefault('Status', 'Under Review')
                        subpolicy_data.setdefault('CreatedByName', policy.CreatedByName)
                        subpolicy_data['CreatedByDate'] = datetime.date.today()  # Always use current date
 
                        subpolicy_serializer = SubPolicySerializer(data=subpolicy_data)
                        if not subpolicy_serializer.is_valid():
                            return Response(subpolicy_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                        subpolicy_serializer.save()
                        created_subpolicies_count += 1
 
                # Create a detailed success message
                message = f'Framework "{framework.FrameworkName}" created successfully'
                if created_policies_count > 0:
                    message += f' with {created_policies_count} policies'
                    if created_subpolicies_count > 0:
                        message += f' and {created_subpolicies_count} subpolicies'
                message += '!'
               
                return Response({
                    'message': message,
                    'FrameworkId': framework.FrameworkId,
                    'Version': framework.CurrentVersion
                }, status=status.HTTP_201_CREATED)
 
        except Exception as e:
            return Response({
                'error': 'Error creating framework',
                'details': {
                    'message': str(e),
                    'traceback': traceback.format_exc()
                }
            }, status=status.HTTP_400_BAD_REQUEST)
 
 

"""
@api GET /api/frameworks/{pk}/
Returns a specific framework by ID if it has Status='Approved' and ActiveInactive='Active'.

@api PUT /api/frameworks/{pk}/
Updates an existing framework. Only frameworks with Status='Approved' and ActiveInactive='Active' can be updated.

Example payload:
{
  "FrameworkName": "ISO 27001:2022",
  "FrameworkDescription": "Updated Information Security Management System",
  "Category": "Information Security",
  "DocURL": "https://example.com/iso27001-2022",
  "EndDate": "2026-10-01"
}

@api DELETE /api/frameworks/{pk}/
Soft-deletes a framework by setting ActiveInactive='Inactive'.
Also marks all related policies as inactive and all related subpolicies with Status='Inactive'.
"""
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def framework_detail(request, pk):
    framework = get_object_or_404(Framework, FrameworkId=pk)
    
    if request.method == 'GET':
        # Only return details if framework is Approved and Active
        if framework.Status != 'Approved' or framework.ActiveInactive != 'Active':
            return Response({'error': 'Framework is not approved or active'}, status=status.HTTP_403_FORBIDDEN)
        
        # Get all active and approved policies for this framework
        policies = Policy.objects.filter(
            FrameworkId=framework,
            Status='Approved',
            ActiveInactive='Active'
        )
        
        # Get all subpolicies for these policies
        policy_data = []
        for policy in policies:
            policy_dict = {
                'PolicyId': policy.PolicyId,
                'PolicyName': policy.PolicyName,
                'PolicyDescription': policy.PolicyDescription,
                'CurrentVersion': policy.CurrentVersion,
                'StartDate': policy.StartDate,
                'EndDate': policy.EndDate,
                'Department': policy.Department,
                'CreatedByName': policy.CreatedByName,
                'CreatedByDate': policy.CreatedByDate,
                'Applicability': policy.Applicability,
                'DocURL': policy.DocURL,
                'Scope': policy.Scope,
                'Objective': policy.Objective,
                'Identifier': policy.Identifier,
                'PermanentTemporary': policy.PermanentTemporary,
                'subpolicies': []
            }
            
            # Get all subpolicies for this policy
            subpolicies = SubPolicy.objects.filter(PolicyId=policy)
            for subpolicy in subpolicies:
                subpolicy_dict = {
                    'SubPolicyId': subpolicy.SubPolicyId,
                    'SubPolicyName': subpolicy.SubPolicyName,
                    'CreatedByName': subpolicy.CreatedByName,
                    'CreatedByDate': subpolicy.CreatedByDate,
                    'Identifier': subpolicy.Identifier,
                    'Description': subpolicy.Description,
                    'Status': subpolicy.Status,
                    'PermanentTemporary': subpolicy.PermanentTemporary,
                    'Control': subpolicy.Control
                }
                policy_dict['subpolicies'].append(subpolicy_dict)
            
            policy_data.append(policy_dict)
        
        # Create response data
        response_data = {
            'FrameworkId': framework.FrameworkId,
            'FrameworkName': framework.FrameworkName,
            'CurrentVersion': framework.CurrentVersion,
            'FrameworkDescription': framework.FrameworkDescription,
            'EffectiveDate': framework.EffectiveDate,
            'CreatedByName': framework.CreatedByName,
            'CreatedByDate': framework.CreatedByDate,
            'Category': framework.Category,
            'DocURL': framework.DocURL,
            'Identifier': framework.Identifier,
            'StartDate': framework.StartDate,
            'EndDate': framework.EndDate,
            'Status': framework.Status,
            'ActiveInactive': framework.ActiveInactive,
            'policies': policy_data
        }
        
        return Response(response_data)
    
    elif request.method == 'PUT':
        # Check if framework is approved and active before allowing update
        if framework.Status != 'Approved' or framework.ActiveInactive != 'Active':
            return Response({'error': 'Only approved and active frameworks can be updated'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            with transaction.atomic():
                serializer = FrameworkSerializer(framework, data=request.data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        'message': 'Framework updated successfully',
                        'FrameworkId': framework.FrameworkId,
                        'CurrentVersion': framework.CurrentVersion
                    })
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_info = {
                'error': str(e),
                'traceback': traceback.format_exc()
            }
            return Response({'error': 'Error updating framework', 'details': error_info}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        try:
            with transaction.atomic():
                # Instead of deleting, set ActiveInactive to 'Inactive'
                framework.ActiveInactive = 'Inactive'
                framework.save()
                
                # Set all related policies to inactive
                policies = Policy.objects.filter(FrameworkId=framework)
                for policy in policies:
                    policy.ActiveInactive = 'Inactive'
                    policy.save()
                    
                    # Update Status of subpolicies since they don't have ActiveInactive field
                    subpolicies = SubPolicy.objects.filter(PolicyId=policy)
                    for subpolicy in subpolicies:
                        subpolicy.Status = 'Inactive'
                        subpolicy.save()
                
                return Response({'message': 'Framework and related policies marked as inactive'}, status=status.HTTP_200_OK)
        except Exception as e:
            error_info = {
                'error': str(e),
                'traceback': traceback.format_exc()
            }
            return Response({'error': 'Error marking framework as inactive', 'details': error_info}, status=status.HTTP_400_BAD_REQUEST)

# Policy CRUD operations

"""
@api GET /api/policies/{pk}/
Returns a specific policy by ID if it has Status='Approved' and ActiveInactive='Active',
and its parent framework has Status='Approved' and ActiveInactive='Active'.

@api PUT /api/policies/{pk}/
Updates an existing policy. Only policies with Status='Approved' and ActiveInactive='Active'
whose parent framework is also Approved and Active can be updated.

Example payload:
{
  "PolicyName": "Updated Access Control Policy",
  "PolicyDescription": "Enhanced guidelines for access control management with additional security measures",
  "StartDate": "2023-12-01",
  "EndDate": "2025-12-01",
  "Department": "IT,Security",
  "Scope": "All IT systems and cloud services",
  "Objective": "Ensure proper access control with improved security"
}

@api DELETE /api/policies/{pk}/
Soft-deletes a policy by setting ActiveInactive='Inactive'.
Also marks all related subpolicies with Status='Inactive'.
"""
@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def policy_detail(request, pk):
    policy = get_object_or_404(Policy, PolicyId=pk)
    
    if request.method == 'GET':
        # Only return details if policy is Approved and Active
        if policy.Status != 'Approved' or policy.ActiveInactive != 'Active':
            return Response({'error': 'Policy is not approved or active'}, status=status.HTTP_403_FORBIDDEN)
        
        # Get framework to check if it's approved and active
        framework = policy.FrameworkId
        if framework.Status != 'Approved' or framework.ActiveInactive != 'Active':
            return Response({'error': 'Framework is not approved or active'}, status=status.HTTP_403_FORBIDDEN)
        
        serializer = PolicySerializer(policy)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Check if policy is approved and active before allowing update
        if policy.Status != 'Approved' or policy.ActiveInactive != 'Active':
            return Response({'error': 'Only approved and active policies can be updated'}, status=status.HTTP_403_FORBIDDEN)
        
        # Check if framework is approved and active
        framework = policy.FrameworkId
        if framework.Status != 'Approved' or framework.ActiveInactive != 'Active':
            return Response({'error': 'Framework is not approved or active'}, status=status.HTTP_403_FORBIDDEN)
        
        try:
            with transaction.atomic():
                # Add status and ActiveInactive to request data
                update_data = request.data.copy()
                update_data['Status'] = 'Under Review'
                update_data['ActiveInactive'] = 'Inactive'
                
                serializer = PolicySerializer(policy, data=update_data, partial=True)
                if serializer.is_valid():
                    serializer.save()
                    return Response({
                        'message': 'Policy updated successfully and set to Under Review',
                        'PolicyId': policy.PolicyId,
                        'CurrentVersion': policy.CurrentVersion,
                        'Status': 'Under Review',
                        'ActiveInactive': 'Inactive'
                    })
                else:
                    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            error_info = {
                'error': str(e),
                'traceback': traceback.format_exc()
            }
            return Response({'error': 'Error updating policy', 'details': error_info}, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        try:
            with transaction.atomic():
                # Instead of deleting, set ActiveInactive to 'Inactive'
                policy.ActiveInactive = 'Inactive'
                policy.save()
                
                # Update Status of subpolicies since they don't have ActiveInactive field
                subpolicies = SubPolicy.objects.filter(PolicyId=policy)
                for subpolicy in subpolicies:
                    subpolicy.Status = 'Inactive'
                    subpolicy.save()
                
                return Response({'message': 'Policy and related subpolicies marked as inactive'}, status=status.HTTP_200_OK)
        except Exception as e:
            error_info = {
                'error': str(e),
                'traceback': traceback.format_exc()
            }
            return Response({'error': 'Error marking policy as inactive', 'details': error_info}, status=status.HTTP_400_BAD_REQUEST)

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
            # Set framework ID and default values in the request data
            policy_data = request.data.copy()
            policy_data['FrameworkId'] = framework.FrameworkId
            policy_data['CurrentVersion'] = framework.CurrentVersion  # Use framework's version
            
            # Set default values if not provided
            if 'Status' not in policy_data:
                policy_data['Status'] = 'Under Review'
            if 'ActiveInactive' not in policy_data:
                policy_data['ActiveInactive'] = 'Inactive'
            if 'CreatedByName' not in policy_data or not policy_data['CreatedByName']:
                policy_data['CreatedByName'] = framework.CreatedByName
            if 'CreatedByDate' not in policy_data:
                policy_data['CreatedByDate'] = datetime.date.today()
            if 'Reviewer' not in policy_data:
                policy_data['Reviewer'] = None
           
            print("DEBUG: Policy data before serialization:", policy_data)
            policy_serializer = PolicySerializer(data=policy_data)
            print("DEBUG: validating policy serializer")
            if not policy_serializer.is_valid():
                print("Policy serializer errors:", policy_serializer.errors)
                return Response({
                    'error': 'Policy validation failed',
                    'details': policy_serializer.errors
                }, status=status.HTTP_400_BAD_REQUEST)
            print("DEBUG: serializer is valid")
 
            policy = policy_serializer.save()
 
            # Get reviewer ID directly from the request data
            reviewer_id = policy_data.get('Reviewer')  # This should be a UserId (number)
           
            # Get reviewer's name for the Policy table
            reviewer_name = None
            if reviewer_id:
                try:
                    reviewer_id = int(reviewer_id)  # Ensure reviewer_id is an integer
                    reviewer_obj = Users.objects.filter(UserId=reviewer_id).first()
                    if reviewer_obj:
                        reviewer_name = reviewer_obj.UserName
                        # Store reviewer name in the policy object
                        policy.Reviewer = reviewer_name
                        policy.save()
                except (ValueError, TypeError):
                    print(f"Warning: Invalid reviewer ID format: {reviewer_id}")
 
            # Get user id from CreatedByName
            created_by_name = policy_data.get('CreatedByName')
            user_obj = Users.objects.filter(UserName=created_by_name).first()
            user_id = user_obj.UserId if user_obj else None
 
            if user_id is None:
                print(f"Warning: CreatedBy user not found for: {created_by_name}")
            if reviewer_id is None:
                print("Warning: Reviewer id missing in request data")

            try:
                print("Creating PolicyVersion with:", {
                    "PolicyId": policy.PolicyId,
                    "Version": policy.CurrentVersion,
                    "PolicyName": policy.PolicyName,
                    "CreatedBy": policy.CreatedByName,
                    "CreatedDate": policy.CreatedByDate,
                    "PreviousVersionId": None
                })
 
                policy_version = PolicyVersion(
                    PolicyId=policy,
                    Version=policy.CurrentVersion,
                    PolicyName=policy.PolicyName,
                    CreatedBy=policy.CreatedByName,
                    CreatedDate=policy.CreatedByDate,
                    PreviousVersionId=None
                )
                policy_version.save()
            except Exception as e:
                print("Error creating PolicyVersion:", str(e))
                raise
 
           
            # Create subpolicies if provided
            subpolicies_data = request.data.get('subpolicies', [])
            created_subpolicies_count = 0
           
            for subpolicy_data in subpolicies_data:
                # Set policy ID and default values
                subpolicy_data = subpolicy_data.copy() if isinstance(subpolicy_data, dict) else {}
                subpolicy_data['PolicyId'] = policy.PolicyId
                if 'CreatedByName' not in subpolicy_data or not subpolicy_data['CreatedByName']:
                    subpolicy_data['CreatedByName'] = policy.CreatedByName
                if 'CreatedByDate' not in subpolicy_data:
                    subpolicy_data['CreatedByDate'] = datetime.date.today()
                if 'Status' not in subpolicy_data:
                    subpolicy_data['Status'] = 'Under Review'
                if 'PermanentTemporary' not in subpolicy_data:
                    subpolicy_data['PermanentTemporary'] = 'Permanent'
               
                print("DEBUG: SubPolicy data before serialization:", subpolicy_data)
                subpolicy_serializer = SubPolicySerializer(data=subpolicy_data)
                if not subpolicy_serializer.is_valid():
                    print("SubPolicy serializer errors:", subpolicy_serializer.errors)
                    return Response({
                        'error': 'SubPolicy validation failed',
                        'details': subpolicy_serializer.errors
                    }, status=status.HTTP_400_BAD_REQUEST)
                subpolicy_serializer.save()
                created_subpolicies_count += 1
               
            # Create a detailed success message
            message = 'Policy added to framework successfully'
            if created_subpolicies_count > 0:
                message += f' with {created_subpolicies_count} subpolicies'
            message += '!'
           
            return Response({
                'message': message,
                'PolicyId': policy.PolicyId,
                'FrameworkId': framework.FrameworkId,
                'Version': policy.CurrentVersion
            }, status=status.HTTP_201_CREATED)
    except Exception as e:
        error_info = {
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        print("DEBUG: Error details:", error_info)
        return Response({
            'error': 'Error adding policy to framework',
            'details': error_info
        }, status=status.HTTP_400_BAD_REQUEST)

"""
@api POST /api/policies/{policy_id}/subpolicies/
Adds a new subpolicy to an existing policy.
New subpolicies are created with Status='Under Review' by default.

Example payload:
{
  "SubPolicyName": "Multi-Factor Authentication",
  "Identifier": "MFA-001",
  "Description": "Requirements for multi-factor authentication",
  "PermanentTemporary": "Permanent",
  "Control": "Implement MFA for all admin access and sensitive operations"
}
"""
@api_view(['POST'])
@permission_classes([AllowAny])
def add_policy_to_framework(request, framework_id):
    framework = get_object_or_404(Framework, FrameworkId=framework_id)
   
    try:
        with transaction.atomic():
            # Set framework ID and default values in the request data
            policy_data = request.data.copy()
            policy_data['FrameworkId'] = framework.FrameworkId
            policy_data['CurrentVersion'] = framework.CurrentVersion  # Use framework's version
            if 'Status' not in policy_data:
                policy_data['Status'] = 'Under Review'
            if 'ActiveInactive' not in policy_data:
                policy_data['ActiveInactive'] = 'Inactive'
            if 'CreatedByName' not in policy_data:
                policy_data['CreatedByName'] = framework.CreatedByName
            if 'CreatedByDate' not in policy_data:
                policy_data['CreatedByDate'] = datetime.date.today()
           
            policy_serializer = PolicySerializer(data=policy_data)
            print("DEBUG: validating policy serializer")
            if not policy_serializer.is_valid():
                print("Policy serializer errors:", policy_serializer.errors)
                return Response(policy_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            print("DEBUG: serializer is valid")
 
            policy = policy_serializer.save()
 
            # Get reviewer ID directly from the request data
            reviewer_id = policy_data.get('Reviewer')  # Changed from request.data to policy_data
           
            # Get reviewer's name for the Policy table
            reviewer_name = None
            if reviewer_id:
                reviewer_obj = Users.objects.filter(UserId=reviewer_id).first()
                if reviewer_obj:
                    reviewer_name = reviewer_obj.UserName
                    # Store reviewer name in the policy object
                    policy.Reviewer = reviewer_name
                    policy.save()
 
            # Get user id from CreatedByName
            created_by_name = policy_data.get('CreatedByName')
            user_obj = Users.objects.filter(UserName=created_by_name).first()
            user_id = user_obj.UserId if user_obj else None
 
            if user_id is None:
                print(f"Warning: CreatedBy user not found for: {created_by_name}")
            if reviewer_id is None:
                print("Warning: Reviewer id missing in request data")
 
            # No policy approval logic here - removed completely
 
            try:
                print("Creating PolicyVersion with:", {
                    "PolicyId": policy.PolicyId,
                    "Version": policy.CurrentVersion,
                    "PolicyName": policy.PolicyName,
                    "CreatedBy": policy.CreatedByName,
                    "CreatedDate": policy.CreatedByDate,
                    "PreviousVersionId": None
                })
 
                policy_version = PolicyVersion(
                    PolicyId=policy,
                    Version=policy.CurrentVersion,
                    PolicyName=policy.PolicyName,
                    CreatedBy=policy.CreatedByName,
                    CreatedDate=policy.CreatedByDate,
                    PreviousVersionId=None
                )
                policy_version.save()
            except Exception as e:
                print("Error creating PolicyVersion:", str(e))
                raise
 
            # Create subpolicies if provided
            subpolicies_data = request.data.get('subpolicies', [])
            created_subpolicies_count = 0
           
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
                    print("SubPolicy serializer errors:", subpolicy_serializer.errors)  # Add this debug
                    return Response(subpolicy_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                subpolicy_serializer.save()
                created_subpolicies_count += 1
               
            # Create a detailed success message
            message = 'Policy added to framework successfully'
            if created_subpolicies_count > 0:
                message += f' with {created_subpolicies_count} subpolicies'
            message += '!'
           
            return Response({
                'message': message,
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
            queryset = queryset.filter(SubPolicy__Policy__Framework_id=framework_id)

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

        # Calculate total findings
        total_findings = queryset.filter(IsRisk=True).count()

        return Response({
            'success': True,
            'data': {
                'summary': {
                    'status_counts': status_counts,
                    'criticality_counts': criticality_counts,
                    'total_count': queryset.count(),
                    'total_findings': total_findings
                }
            }
        })

    except Exception as e:
        print(f"Error in get_compliance_dashboard: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_compliances_by_subpolicy(request, subpolicy_id):
    try:
        # Verify subpolicy exists first
        subpolicy = get_object_or_404(SubPolicy, SubPolicyId=subpolicy_id)
       
        # Get all compliances for this subpolicy
        compliances = Compliance.objects.filter(SubPolicy_id=subpolicy_id)
       
        # Create a dictionary to store compliance groups
        compliance_groups = {}
       
        # First pass: Create groups based on Identifier
        for compliance in compliances:
            if compliance.Identifier not in compliance_groups:
                compliance_groups[compliance.Identifier] = []
            compliance_groups[compliance.Identifier].append(compliance)
       
        # Second pass: Sort each group by version number
        for identifier in compliance_groups:
            compliance_groups[identifier].sort(
                key=lambda x: float(x.ComplianceVersion),
                reverse=True
            )
       
        # Convert to list and sort groups by latest version's creation date
        sorted_groups = sorted(
            compliance_groups.values(),
            key=lambda group: group[0].CreatedByDate,
            reverse=True
        )
       
        # Flatten the groups while maintaining order
        serialized_compliances = []
        for group in sorted_groups:
            group_data = []
            for compliance in group:
                serializer = ComplianceListSerializer(compliance)
                data = serializer.data
                # Add group identifier to help frontend
                data['group_identifier'] = compliance.Identifier
                group_data.append(data)
            serialized_compliances.extend(group_data)
       
        return Response({
            'success': True,
            'data': serialized_compliances
        })
    except SubPolicy.DoesNotExist:
        return Response({
            'success': False,
            'message': f'SubPolicy with id {subpolicy_id} not found'
        }, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error in get_compliances_by_subpolicy: {str(e)}")
        return Response({
            'success': False,
            'message': 'An error occurred while fetching compliances'
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
        print(f"Received review data - ApprovedNot: {approved_not}")
       
        # Create new approval version
        new_version = "r1"
        try:
            r_versions = [int(pa.Version[1:]) for pa in PolicyApproval.objects.filter(
                Identifier=approval.Identifier
            ) if pa.Version and pa.Version.startswith('r') and pa.Version[1:].isdigit()]
            if r_versions:
                new_version = f"r{max(r_versions) + 1}"
        except Exception as e:
            print(f"Error determining version: {e}")
       
        # Create new approval record with ApprovedDate if approved
        new_approval_data = {
            'Identifier': approval.Identifier,
            'ExtractedData': extracted_data,
            'UserId': approval.UserId,
            'ReviewerId': approval.ReviewerId,
            'ApprovedNot': approved_not,
            'Version': new_version,
            'ApprovedDate': timezone.now() if approved_not is True else None
        }
       
        # Create new approval record
        new_approval = PolicyApproval.objects.create(**new_approval_data)
       
        if 'SubPolicy' in extracted_data:
            try:
                # Find the compliance being reviewed
                current_compliance = Compliance.objects.filter(
                    SubPolicy_id=extracted_data.get('SubPolicy'),
                    Identifier=approval.Identifier,
                    Status='Under Review'
                ).first()
               
                if current_compliance:
                    print(f"Processing compliance: {current_compliance.ComplianceId}")
                   
                    if approved_not is True:
                        # If approved, set current to Active and previous to Inactive
                        current_compliance.Status = 'Approved'
                        current_compliance.ActiveInactive = 'Active'
                       
                        # Get and deactivate the previous version if it exists
                        if current_compliance.PreviousComplianceVersionId:
                            try:
                                prev_compliance = current_compliance.PreviousComplianceVersionId
                                if prev_compliance.ActiveInactive == 'Active':
                                    prev_compliance.ActiveInactive = 'Inactive'
                                    prev_compliance.save()
                                    print(f"Deactivated previous version: {prev_compliance.ComplianceId}")
                            except Exception as e:
                                print(f"Error deactivating previous version: {e}")
                               
                    elif approved_not is False:
                        # If rejected, just mark as rejected and keep inactive
                        current_compliance.Status = 'Rejected'
                        current_compliance.ActiveInactive = 'Inactive'
                   
                    current_compliance.save()
                    print(f"Updated compliance {current_compliance.ComplianceId}: Status={current_compliance.Status}, ActiveInactive={current_compliance.ActiveInactive}")
           
            except Exception as e:
                print(f"Error updating compliance: {e}")
                import traceback
                traceback.print_exc()
       
        return Response({
            'message': 'Compliance review submitted successfully',
            'ApprovalId': new_approval.ApprovalId,
            'Version': new_approval.Version,
            'ApprovedDate': new_approval.ApprovedDate.isoformat() if new_approval.ApprovedDate else None
        })
       
    except Exception as e:
        print(f"Error in submit_compliance_review: {e}")
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
            Identifier=approval.Identifier,  # Using the correct field name
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
            'message': 'Compliance review resubmitted successfully',
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
 
@api_view(['GET'])
def get_compliance_versioning(request):
    """
    Returns compliance versioning data for the frontend.
    """
    try:
        # You can customize this to return whatever versioning data you need
        # For now, we'll just return a success message
        return Response({
            'success': True,
            'message': 'Compliance versioning API endpoint',
            'data': []
        })
    except Exception as e:
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
def get_policy_approvals_by_reviewer(request):
    try:
        # Get reviewer ID from request or use default
        reviewer_id = request.query_params.get('reviewer_id', 2)
        print(f"Fetching approvals for reviewer_id: {reviewer_id}")
        
        # First get all compliances that are Under Review
        under_review_compliances = Compliance.objects.filter(
            Status='Under Review'
        ).select_related('SubPolicy')
        
        print(f"Found {under_review_compliances.count()} compliances under review")
        
        # Get their corresponding policy approvals
        approvals = []
        for compliance in under_review_compliances:
            # Get the latest policy approval for this compliance
            latest_approval = PolicyApproval.objects.filter(
                Identifier=compliance.Identifier,
                ReviewerId=reviewer_id,
            ).order_by('-ApprovalId').first()
            
            if latest_approval and latest_approval.ApprovedNot is None:
                # If we have a pending approval, use it
                approval_dict = {
                    'ApprovalId': latest_approval.ApprovalId,
                    'Identifier': latest_approval.Identifier,
                    'ExtractedData': latest_approval.ExtractedData,
                    'UserId': latest_approval.UserId,
                    'ReviewerId': latest_approval.ReviewerId,
                    'ApprovedNot': latest_approval.ApprovedNot,
                    'Version': latest_approval.Version,
                    'ApprovedDate': latest_approval.ApprovedDate.isoformat() if latest_approval.ApprovedDate else None
                }
                approvals.append(approval_dict)
            elif not latest_approval:
                # If no approval exists, create one
                extracted_data = {
                    'type': 'compliance',
                    'ComplianceItemDescription': compliance.ComplianceItemDescription,
                    'IsRisk': compliance.IsRisk,
                    'PossibleDamage': compliance.PossibleDamage,
                    'mitigation': compliance.mitigation,
                    'Criticality': compliance.Criticality,
                    'MandatoryOptional': compliance.MandatoryOptional,
                    'ManualAutomatic': compliance.ManualAutomatic,
                    'Impact': compliance.Impact,
                    'Probability': compliance.Probability,
                    'MaturityLevel': compliance.MaturityLevel,
                    'ActiveInactive': compliance.ActiveInactive,
                    'PermanentTemporary': compliance.PermanentTemporary,
                    'Status': compliance.Status,
                    'ComplianceVersion': compliance.ComplianceVersion,
                    'CreatedByName': compliance.CreatedByName,
                    'CreatedByDate': compliance.CreatedByDate.isoformat() if compliance.CreatedByDate else None,
                    'SubPolicy': compliance.SubPolicy_id,
                    'compliance_approval': {
                        'approved': None,
                        'remarks': ''
                    }
                }
                
                new_approval = PolicyApproval.objects.create(
                    Identifier=compliance.Identifier,
                    ExtractedData=extracted_data,
                    UserId=1,  # System user
                    ReviewerId=reviewer_id,
                    ApprovedNot=None,
                    Version="u1"
                )
                
                approval_dict = {
                    'ApprovalId': new_approval.ApprovalId,
                    'Identifier': new_approval.Identifier,
                    'ExtractedData': extracted_data,
                    'UserId': new_approval.UserId,
                    'ReviewerId': new_approval.ReviewerId,
                    'ApprovedNot': new_approval.ApprovedNot,
                    'Version': new_approval.Version,
                    'ApprovedDate': None
                }
                approvals.append(approval_dict)
        
        print(f"Total approvals to return: {len(approvals)}")
        
        # Get counts
        counts = {
            'pending': sum(1 for a in approvals if a['ApprovedNot'] is None),
            'approved': PolicyApproval.objects.filter(ReviewerId=reviewer_id, ApprovedNot=True).count(),
            'rejected': PolicyApproval.objects.filter(ReviewerId=reviewer_id, ApprovedNot=False).count()
        }
        
        print(f"Approval counts: {counts}")
        
        return Response({
            'success': True,
            'data': approvals,
            'counts': counts
        })
        
    except Exception as e:
        print(f"Error in get_policy_approvals_by_reviewer: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
 
@api_view(['GET'])
def get_rejected_approvals(request, reviewer_id):
    try:
        # Get all policy approvals that have been rejected for this reviewer
        approvals = PolicyApproval.objects.filter(
            ReviewerId=reviewer_id,
            ApprovedNot=False
        ).order_by('-ApprovalId')
       
        # Convert to list for JSON serialization
        approvals_list = []
        for approval in approvals:
            approval_dict = {
                'ApprovalId': approval.ApprovalId,
                'Identifier': approval.Identifier,
                'ExtractedData': approval.ExtractedData,
                'UserId': approval.UserId,
                'ReviewerId': approval.ReviewerId,
                'ApprovedNot': approval.ApprovedNot,
                'Version': approval.Version,
                'rejection_reason': approval.ExtractedData.get('compliance_approval', {}).get('remarks', '')
            }
            approvals_list.append(approval_dict)
           
        return Response(approvals_list)
       
    except Exception as e:
        print("Error in get_rejected_approvals:", str(e))
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
 
@api_view(['GET'])
def get_all_users(request):
    try:
        from .models import User
        # Get all users except the system user (UserId=1)
        users = User.objects.exclude(UserId=1)
        users_list = [{"UserId": user.UserId, "UserName": user.UserName} for user in users]
        return Response({'success': True, 'users': users_list})
    except Exception as e:
        return Response({'success': False, 'message': str(e)}, status=500)
 
@api_view(['POST'])
def toggle_compliance_version(request, compliance_id):
    try:
        # Get the target compliance
        compliance = get_object_or_404(Compliance, ComplianceId=compliance_id)
       
        # Only allow toggling if compliance is approved
        if compliance.Status != 'Approved':
            return Response({
                'success': False,
                'message': 'Only approved compliances can be toggled'
            }, status=status.HTTP_400_BAD_REQUEST)
 
        # Function to get all related versions (both previous and next)
        def get_all_versions(comp):
            versions = []
           
            # Get all previous versions
            current = comp
            while current.PreviousComplianceVersionId:
                versions.append(current.PreviousComplianceVersionId)
                current = current.PreviousComplianceVersionId
           
            # Get all next versions
            current = comp
            next_versions = Compliance.objects.filter(PreviousComplianceVersionId=current.ComplianceId)
            while next_versions.exists():
                next_version = next_versions.first()
                versions.append(next_version)
                next_versions = Compliance.objects.filter(PreviousComplianceVersionId=next_version.ComplianceId)
           
            # Add the current compliance
            versions.append(comp)
            return versions
 
        # Get all versions
        all_versions = get_all_versions(compliance)
       
        # Determine new status
        new_status = 'Active' if compliance.ActiveInactive == 'Inactive' else 'Inactive'
       
        # Update all versions
        for version in all_versions:
            if version.ComplianceId == compliance_id:
                # Set the target compliance to the new status
                version.ActiveInactive = new_status
            else:
                # Set all other versions to inactive
                version.ActiveInactive = 'Inactive'
            version.save()
       
        return Response({
            'success': True,
            'message': f'Successfully updated compliance version statuses. Version {compliance.ComplianceVersion} is now {new_status}.',
            'active_version': {
                'ComplianceId': compliance.ComplianceId,
                'Version': compliance.ComplianceVersion,
                'Status': new_status
            }
        })
       
    except Exception as e:
        print(f"Error in toggle_compliance_version: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
def test_analytics_endpoint(request):
    return Response({
        'success': True,
        'message': 'Analytics endpoint is reachable'
    })

@api_view(['POST'])
@csrf_exempt
@permission_classes([AllowAny])
def get_compliance_analytics(request):
    try:
        print("Received analytics request with data:", request.data)
        x_axis = request.data.get('xAxis')
        y_axis = request.data.get('yAxis')

        if not x_axis or not y_axis:
            return Response({
                'success': False,
                'message': 'Both X and Y axis parameters are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        # Get base queryset
        queryset = Compliance.objects.all()
        
        # Get counts for dashboard metrics
        total_compliances = queryset.count()
        approved_compliances = queryset.filter(Status='Approved').count()
        active_compliances = queryset.filter(ActiveInactive='Active').count()
        under_review_compliances = queryset.filter(Status='Under Review').count()

        # Calculate approval rate
        approval_rate = (approved_compliances / total_compliances * 100) if total_compliances > 0 else 0

        # Initialize chart data based on Y axis selection
        labels = []
        data = []

        if y_axis == 'Criticality':
            counts = queryset.values('Criticality').annotate(
                count=models.Count('ComplianceId')
            ).exclude(Criticality__isnull=True).exclude(Criticality='')
            labels = ['High', 'Medium', 'Low']
            data = [
                next((item['count'] for item in counts if item['Criticality'] == 'High'), 0),
                next((item['count'] for item in counts if item['Criticality'] == 'Medium'), 0),
                next((item['count'] for item in counts if item['Criticality'] == 'Low'), 0)
            ]

        elif y_axis == 'Status':
            counts = queryset.values('Status').annotate(
                count=models.Count('ComplianceId')
            ).exclude(Status__isnull=True).exclude(Status='')
            labels = ['Approved', 'Under Review', 'Rejected', 'Active']
            data = [
                next((item['count'] for item in counts if item['Status'] == 'Approved'), 0),
                next((item['count'] for item in counts if item['Status'] == 'Under Review'), 0),
                next((item['count'] for item in counts if item['Status'] == 'Rejected'), 0),
                next((item['count'] for item in counts if item['Status'] == 'Active'), 0)
            ]

        elif y_axis == 'ActiveInactive':
            counts = queryset.values('ActiveInactive').annotate(
                count=models.Count('ComplianceId')
            ).exclude(ActiveInactive__isnull=True).exclude(ActiveInactive='')
            labels = ['Active', 'Inactive']
            data = [
                next((item['count'] for item in counts if item['ActiveInactive'] == 'Active'), 0),
                next((item['count'] for item in counts if item['ActiveInactive'] == 'Inactive'), 0)
            ]

        elif y_axis == 'ManualAutomatic':
            counts = queryset.values('ManualAutomatic').annotate(
                count=models.Count('ComplianceId')
            ).exclude(ManualAutomatic__isnull=True).exclude(ManualAutomatic='')
            labels = ['Manual', 'Automatic']
            data = [
                next((item['count'] for item in counts if item['ManualAutomatic'] == 'Manual'), 0),
                next((item['count'] for item in counts if item['ManualAutomatic'] == 'Automatic'), 0)
            ]

        elif y_axis == 'MandatoryOptional':
            counts = queryset.values('MandatoryOptional').annotate(
                count=models.Count('ComplianceId')
            ).exclude(MandatoryOptional__isnull=True).exclude(MandatoryOptional='')
            labels = ['Mandatory', 'Optional']
            data = [
                next((item['count'] for item in counts if item['MandatoryOptional'] == 'Mandatory'), 0),
                next((item['count'] for item in counts if item['MandatoryOptional'] == 'Optional'), 0)
            ]

        elif y_axis == 'MaturityLevel':
            counts = queryset.values('MaturityLevel').annotate(
                count=models.Count('ComplianceId')
            ).exclude(MaturityLevel__isnull=True).exclude(MaturityLevel='')
            labels = ['Initial', 'Developing', 'Defined', 'Managed', 'Optimizing']
            data = [
                next((item['count'] for item in counts if item['MaturityLevel'] == level), 0)
                for level in labels
            ]

        # Prepare dashboard data
        dashboard_data = {
            'status_counts': {
                'approved': approved_compliances,
                'active': active_compliances,
                'under_review': under_review_compliances
            },
            'total_count': total_compliances,
            'total_findings': queryset.filter(IsRisk=True).count(),
            'approval_rate': round(approval_rate, 2)
        }

        # Prepare chart data
        chart_data = {
            'labels': labels,
            'datasets': [{
                'label': f'Compliance by {y_axis.replace("By ", "")}',
                'data': data
            }]
        }

        print("Sending response with dashboard_data:", dashboard_data)
        print("Chart data:", chart_data)

        return Response({
            'success': True,
            'chartData': chart_data,
            'dashboardData': dashboard_data
        })

    except Exception as e:
        print(f"Error in get_compliance_analytics: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

 
 #---------------------------------KPI Dashboard---------------------------------
 
@api_view(['GET'])
def get_compliance_kpi(request):
    try:
        # Get all compliances
        compliances = Compliance.objects.all()
        
        # Calculate KPIs
        total_compliances = compliances.count()
        active_compliances = compliances.filter(ActiveInactive='Active').count()
        approved_compliances = compliances.filter(Status='Approved').count()
        
        # Calculate compliance rate
        compliance_rate = (approved_compliances / total_compliances * 100) if total_compliances > 0 else 0
        
        # Get risk distribution
        high_risk = compliances.filter(Criticality='High').count()
        medium_risk = compliances.filter(Criticality='Medium').count()
        low_risk = compliances.filter(Criticality='Low').count()
        
        # Calculate maturity levels distribution
        maturity_levels = {
            'Initial': compliances.filter(MaturityLevel='Initial').count(),
            'Developing': compliances.filter(MaturityLevel='Developing').count(),
            'Defined': compliances.filter(MaturityLevel='Defined').count(),
            'Managed': compliances.filter(MaturityLevel='Managed').count(),
            'Optimizing': compliances.filter(MaturityLevel='Optimizing').count()
        }
        
        # Calculate average maturity score
        maturity_scores = {
            'Initial': 1,
            'Developing': 2,
            'Defined': 3,
            'Managed': 4,
            'Optimizing': 5
        }
        total_score = sum(maturity_scores[level] * count for level, count in maturity_levels.items())
        avg_maturity = total_score / total_compliances if total_compliances > 0 else 0
        
        # Get control types distribution
        manual_controls = compliances.filter(ManualAutomatic='Manual').count()
        automatic_controls = compliances.filter(ManualAutomatic='Automatic').count()
        
        # Get mandatory vs optional distribution
        mandatory_controls = compliances.filter(MandatoryOptional='Mandatory').count()
        optional_controls = compliances.filter(MandatoryOptional='Optional').count()
        
        return Response({
            'success': True,
            'data': {
                'compliance_rate': round(compliance_rate, 2),
                'active_controls': active_compliances,
                'maturity_score': round(avg_maturity, 2),
                'risk_distribution': {
                    'high': high_risk,
                    'medium': medium_risk,
                    'low': low_risk
                },
                'maturity_levels': maturity_levels,
                'control_types': {
                    'manual': manual_controls,
                    'automatic': automatic_controls
                },
                'control_requirements': {
                    'mandatory': mandatory_controls,
                    'optional': optional_controls
                },
                'total_compliances': total_compliances,
                'approved_compliances': approved_compliances
            }
        })
        
    except Exception as e:
        print(f"Error in get_compliance_kpi: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_maturity_level_kpi(request):
    try:
        # Get only active and approved compliances
        compliances = Compliance.objects.filter(
            ActiveInactive='Active',
            Status='Approved'
        )
        
        # Calculate counts for each maturity level
        maturity_counts = {
            'Initial': compliances.filter(MaturityLevel='Initial').count(),
            'Developing': compliances.filter(MaturityLevel='Developing').count(),
            'Defined': compliances.filter(MaturityLevel='Defined').count(),
            'Managed': compliances.filter(MaturityLevel='Managed').count(),
            'Optimizing': compliances.filter(MaturityLevel='Optimizing').count()
        }
        
        return Response({
            'success': True,
            'data': {
                'summary': {
                    'total_by_maturity': maturity_counts,
                    'total_compliances': compliances.count()
                }
            }
        })
        
    except Exception as e:
        print(f"Error in get_maturity_level_kpi: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_non_compliance_count(request):
    try:
        # Count records with non-zero count
        non_compliance_count = LastChecklistItemVerified.objects.filter(
            Count__gt=0
        ).count()
        
        return Response({
            'success': True,
            'data': {
                'non_compliance_count': non_compliance_count
            }
        })
        
    except Exception as e:
        print(f"Error in get_non_compliance_count: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_mitigated_risks_count(request):
    try:
        # Count risks that have been mitigated (MitigationStatus = 'Completed')
        mitigated_count = RiskInstance.objects.filter(
            MitigationStatus=RiskInstance.MITIGATION_COMPLETED
        ).count()
        
        return Response({
            'success': True,
            'data': {
                'mitigated_count': mitigated_count
            }
        })
        
    except Exception as e:
        print(f"Error in get_mitigated_risks_count: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_automated_controls_count(request):
    try:
        # Get base queryset for active and approved compliances
        base_query = Compliance.objects.filter(
            Status='Approved',
            ActiveInactive='Active'
        )
        
        # Count automated and manual controls
        automated_count = base_query.filter(ManualAutomatic='Automatic').count()
        manual_count = base_query.filter(ManualAutomatic='Manual').count()
        
        # Calculate percentages
        total = automated_count + manual_count
        automated_percentage = round((automated_count / total * 100) if total > 0 else 0, 1)
        manual_percentage = round((manual_count / total * 100) if total > 0 else 0, 1)
        
        return Response({
            'success': True,
            'data': {
                'automated_count': automated_count,
                'manual_count': manual_count,
                'total_count': total,
                'automated_percentage': automated_percentage,
                'manual_percentage': manual_percentage
            }
        })
        
    except Exception as e:
        print(f"Error in get_automated_controls_count: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def get_non_compliance_repetitions(request):
    try:
        # Get items with non-zero count
        repetitions = LastChecklistItemVerified.objects.filter(
            Count__gt=0
        ).order_by('-Count')

        # Calculate statistics
        total_items = repetitions.count()
        max_repetitions = repetitions.aggregate(max_count=models.Max('Count'))['max_count'] or 0
        avg_repetitions = repetitions.aggregate(avg_count=models.Avg('Count'))['avg_count'] or 0

        # Get distribution of repetitions
        distribution = {}
        for item in repetitions:
            count = item.Count
            if count in distribution:
                distribution[count] += 1
            else:
                distribution[count] = 1

        # Convert distribution to sorted list for chart
        chart_data = [
            {'repetitions': count, 'occurrences': freq}
            for count, freq in sorted(distribution.items())
        ]

        return Response({
            'success': True,
            'data': {
                'total_items': total_items,
                'max_repetitions': max_repetitions,
                'avg_repetitions': round(avg_repetitions, 1),
                'distribution': chart_data
            }
        })
        
    except Exception as e:
        print(f"Error in get_non_compliance_repetitions: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    
#----------------------------------Compliance List---------------------------------
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_frameworks(request):
    """
    API endpoint to get all frameworks for AllPolicies.vue component.
    """
    try:
        frameworks = Framework.objects.all()
       
        frameworks_data = []
        for framework in frameworks:
            framework_data = {
                'id': framework.FrameworkId,
                'name': framework.FrameworkName,
                'category': framework.Category,
                'status': framework.ActiveInactive,
                'description': framework.FrameworkDescription,
                'versions': []
            }
           
            # Get versions for this framework
            versions = FrameworkVersion.objects.filter(FrameworkId=framework)
            version_data = []
            for version in versions:
                version_data.append({
                    'id': version.VersionId,
                    'name': f"v{version.Version}",
                    'version': version.Version
                })
           
            framework_data['versions'] = version_data
            frameworks_data.append(framework_data)
           
        return Response(frameworks_data)
   
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_framework_version_policies(request, version_id):
    """
    API endpoint to get all policies for a specific framework version for AllPolicies.vue component.
    """
    try:
        # Get the framework version
        framework_version = get_object_or_404(FrameworkVersion, VersionId=version_id)
        framework = framework_version.FrameworkId
       
        # Get policies for this framework
        policies = Policy.objects.filter(
            Framework=framework,
            CurrentVersion=framework_version.Version
        )
       
        policies_data = []
        for policy in policies:
            policy_data = {
                'id': policy.PolicyId,
                'name': policy.PolicyName,
                'category': policy.Department,
                'status': policy.Status,
                'description': policy.PolicyDescription,
                'versions': []
            }
           
            # Get versions for this policy
            policy_versions = PolicyVersion.objects.filter(PolicyId=policy)
            versions_data = []
            for version in policy_versions:
                versions_data.append({
                    'id': version.VersionId,
                    'name': f"v{version.Version}",
                    'version': version.Version
                })
           
            policy_data['versions'] = versions_data
            policies_data.append(policy_data)
           
        return Response(policies_data)
       
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_policies(request):
    """
    API endpoint to get all policies for AllPolicies.vue component.
    """
    try:
        # Optional framework filter
        framework_id = request.GET.get('framework_id')
       
        # Start with all policies
        policies_query = Policy.objects.all()
       
        # Apply framework filter if provided
        if framework_id:
            policies_query = policies_query.filter(Framework_id=framework_id)
       
        policies_data = []
        for policy in policies_query:
            policy_data = {
                'id': policy.PolicyId,
                'name': policy.PolicyName,
                'category': policy.Department,
                'status': policy.Status,
                'description': policy.PolicyDescription,
                'versions': []
            }
           
            # Get versions for this policy
            policy_versions = PolicyVersion.objects.filter(PolicyId=policy)
            versions_data = []
            for version in policy_versions:
                versions_data.append({
                    'id': version.VersionId,
                    'name': f"v{version.Version}",
                    'version': version.Version
                })
           
            policy_data['versions'] = versions_data
            policies_data.append(policy_data)
           
        return Response(policies_data)
       
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_policy_versions(request, policy_id):
    """
    API endpoint to get all versions of a specific policy for AllPolicies.vue component.
    Implements a dedicated version that handles version chains through PreviousVersionId.
    """
    try:
        print(f"Request received for policy versions, policy_id: {policy_id}, type: {type(policy_id)}")
       
        # Ensure we have a valid integer ID
        try:
            policy_id = int(policy_id)
        except (ValueError, TypeError):
            return Response({'error': f'Invalid policy ID format: {policy_id}'},
                           status=status.HTTP_400_BAD_REQUEST)
       
        # Get the base policy
        try:
            policy = Policy.objects.get(PolicyId=policy_id)
            print(f"Found policy: {policy.PolicyName} (ID: {policy.PolicyId})")
        except Policy.DoesNotExist:
            print(f"Policy with ID {policy_id} not found")
            return Response({'error': f'Policy with ID {policy_id} not found'},
                           status=status.HTTP_404_NOT_FOUND)
       
        # Get the direct policy version
        try:
            direct_version = PolicyVersion.objects.get(PolicyId=policy)
            print(f"Found direct policy version: {direct_version.VersionId}")
        except PolicyVersion.DoesNotExist:
            print(f"No policy version found for policy ID {policy_id}")
            return Response({'error': f'No version found for policy with ID {policy_id}'},
                           status=status.HTTP_404_NOT_FOUND)
        except PolicyVersion.MultipleObjectsReturned:
            # If there are multiple versions, get all of them
            direct_versions = list(PolicyVersion.objects.filter(PolicyId=policy))
            print(f"Found {len(direct_versions)} direct versions for policy {policy_id}")
            direct_version = direct_versions[0]  # Just use the first one for starting the chain
       
        # Start building version chain
        all_versions = {}
        visited = set()
        to_process = [direct_version.VersionId]
       
        # Find all versions in the chain
        while to_process:
            current_id = to_process.pop(0)
           
            if current_id in visited:
                continue
               
            visited.add(current_id)
           
            try:
                current_version = PolicyVersion.objects.get(VersionId=current_id)
                all_versions[current_id] = current_version
               
                # Follow PreviousVersionId chain backward
                if current_version.PreviousVersionId and current_version.PreviousVersionId not in visited:
                    to_process.append(current_version.PreviousVersionId)
                   
                # Find versions that reference this one as their previous version
                next_versions = PolicyVersion.objects.filter(PreviousVersionId=current_id)
                for next_ver in next_versions:
                    if next_ver.VersionId not in visited:
                        to_process.append(next_ver.VersionId)
            except PolicyVersion.DoesNotExist:
                print(f"Version with ID {current_id} not found")
                continue
       
        versions_data = []
        for version_id, version in all_versions.items():
            try:
                # Get the policy this version belongs to
                version_policy = version.PolicyId
               
                # Count subpolicies for this policy
                subpolicy_count = SubPolicy.objects.filter(PolicyId=version_policy).count()
               
                # Get previous version details if available
                previous_version = None
                if version.PreviousVersionId:
                    try:
                        previous_version = PolicyVersion.objects.get(VersionId=version.PreviousVersionId)
                    except PolicyVersion.DoesNotExist:
                        pass
               
                # Create a descriptive name
                formatted_name = f"{version.PolicyName} v{version.Version}" if version.PolicyName else f"{version_policy.PolicyName} v{version.Version}"
               
                version_data = {
                    'id': version.VersionId,
                    'policy_id': version_policy.PolicyId,
                    'name': formatted_name,
                    'version': version.Version,
                    'category': version_policy.Department or 'General',
                    'status': version_policy.Status or 'Unknown',
                    'description': version_policy.PolicyDescription or '',
                    'created_date': version.CreatedDate,
                    'created_by': version.CreatedBy,
                    'subpolicy_count': subpolicy_count,
                    'previous_version_id': version.PreviousVersionId,
                    'previous_version_name': previous_version.PolicyName + f" v{previous_version.Version}" if previous_version else None
                }
                versions_data.append(version_data)
                print(f"Added version: {version.VersionId} - {formatted_name}, Previous: {version.PreviousVersionId}")
            except Exception as e:
                print(f"Error processing version {version_id}: {str(e)}")
                # Continue to next version
       
        # Sort versions by version number (descending)
        versions_data.sort(key=lambda x: float(x['version']), reverse=True)
 
       
       
        print(f"Returning {len(versions_data)} policy versions")
        return Response(versions_data)
       
    except Exception as e:
        import traceback
        print(f"Error in all_policies_get_policy_versions: {str(e)}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_subpolicies(request):
    """
    API endpoint to get all subpolicies for AllPolicies.vue component.
    """
    try:
        print("Request received for all subpolicies")
       
        # Optional framework filter
        framework_id = request.GET.get('framework_id')
        print(f"Framework filter: {framework_id}")
       
        # Start with all subpolicies
        subpolicies_query = SubPolicy.objects.all()
       
        # If framework filter is provided, filter through policies
        if framework_id:
            try:
                policy_ids = Policy.objects.filter(Framework_id=framework_id).values_list('PolicyId', flat=True)
                print(f"Found {len(policy_ids)} policies for framework {framework_id}")
                subpolicies_query = subpolicies_query.filter(Policy_id__in=policy_ids)
            except Exception as e:
                print(f"Error filtering by framework: {str(e)}")
                # Continue with all subpolicies if framework filtering fails
       
        print(f"Found {subpolicies_query.count()} subpolicies")
       
        subpolicies_data = []
        for subpolicy in subpolicies_query:
            try:
                # Get the policy this subpolicy belongs to
                try:
                    policy = Policy.objects.get(PolicyId=subpolicy.Policy_id)
                    policy_name = policy.PolicyName
                    department = policy.Department
                except Policy.DoesNotExist:
                    print(f"Policy with ID {subpolicy.Policy_id} not found for subpolicy {subpolicy.SubPolicyId}")
                    policy_name = "Unknown Policy"
                    department = "Unknown"
               
                subpolicy_data = {
                    'id': subpolicy.SubPolicyId,
                    'name': subpolicy.SubPolicyName,
                    'category': department or 'General',
                    'status': subpolicy.Status or 'Unknown',
                    'description': subpolicy.Description or '',
                    'control': subpolicy.Control or '',
                    'identifier': subpolicy.Identifier,
                    'permanent_temporary': subpolicy.PermanentTemporary,
                    'policy_id': subpolicy.Policy_id,
                    'policy_name': policy_name,
                    'created_by': subpolicy.CreatedByName,
                    'created_date': subpolicy.CreatedByDate
                }
                subpolicies_data.append(subpolicy_data)
                print(f"Added subpolicy: {subpolicy.SubPolicyId} - {subpolicy.SubPolicyName}")
            except Exception as e:
                print(f"Error processing subpolicy {subpolicy.SubPolicyId}: {str(e)}")
                # Continue to next subpolicy
       
        print(f"Returning {len(subpolicies_data)} subpolicies")
        return Response(subpolicies_data)
       
    except Exception as e:
        import traceback
        print(f"Error in all_policies_get_subpolicies: {str(e)}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_subpolicy_details(request, subpolicy_id):
    """
    API endpoint to get details of a specific subpolicy for AllPolicies.vue component.
    """
    try:
        subpolicy = get_object_or_404(SubPolicy, SubPolicyId=subpolicy_id)
        policy = subpolicy.PolicyId
       
        subpolicy_data = {
            'id': subpolicy.SubPolicyId,
            'name': subpolicy.SubPolicyName,
            'category': policy.Department,
            'status': subpolicy.Status,
            'description': subpolicy.Description,
            'control': subpolicy.Control,
            'identifier': subpolicy.Identifier,
            'permanent_temporary': subpolicy.PermanentTemporary,
            'policy_id': policy.PolicyId,
            'policy_name': policy.PolicyName
        }
       
        return Response(subpolicy_data)
       
    except Exception as e:
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_framework_versions(request, framework_id):
    try:
        print(f"Request received for framework versions, framework_id: {framework_id}")
       
        # Get the base framework
        try:
            framework = Framework.objects.get(FrameworkId=framework_id)
            print(f"Found framework: {framework.FrameworkName}")
        except Framework.DoesNotExist:
            print(f"Framework with ID {framework_id} not found")
            return Response({'error': f'Framework with ID {framework_id} not found'},
                           status=status.HTTP_404_NOT_FOUND)
       
        # Get direct versions that belong to this framework
        direct_versions = list(FrameworkVersion.objects.filter(FrameworkId=framework))
        print(f"Found {len(direct_versions)} direct versions")
       
        versions_data = []
        for version in direct_versions:
            try:
                # Count policies for this framework version
                policy_count = Policy.objects.filter(
                    Framework=framework
                ).count()
               
                # Get previous version details if available
                previous_version = None
                if version.PreviousVersionId:
                    try:
                        previous_version = FrameworkVersion.objects.get(VersionId=version.PreviousVersionId)
                    except FrameworkVersion.DoesNotExist:
                        pass
               
                formatted_name = f"{version.FrameworkName} v{version.Version}"
               
                version_data = {
                    'id': version.VersionId,
                    'name': formatted_name,
                    'version': version.Version,
                    'category': framework.Category or 'General',
                    'status': framework.ActiveInactive or 'Unknown',
                    'description': framework.FrameworkDescription or '',
                    'created_date': version.CreatedDate,
                    'created_by': version.CreatedBy,
                    'policy_count': policy_count,
                    'previous_version_id': version.PreviousVersionId,
                    'previous_version_name': previous_version.FrameworkName + f" v{previous_version.Version}" if previous_version else None,
                    'framework_id': framework.FrameworkId
                }
                versions_data.append(version_data)
                print(f"Added version: {version.VersionId} - {formatted_name}")
            except Exception as e:
                print(f"Error processing version {version.VersionId}: {str(e)}")
                continue
       
        # Sort versions by version number (descending)
        versions_data.sort(key=lambda x: float(x['version']), reverse=True)
       
        print(f"Returning {len(versions_data)} versions")
        return Response(versions_data)
       
    except Exception as e:
        import traceback
        print(f"Error in all_policies_get_framework_versions: {str(e)}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
 
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_policy_version_subpolicies(request, version_id):
    """
    API endpoint to get all subpolicies for a specific policy version for AllPolicies.vue component.
    Implements a dedicated version instead of using the existing get_policy_version_subpolicies function.
    """
    try:
        print(f"Request received for policy version subpolicies, version_id: {version_id}, type: {type(version_id)}")
       
        # Ensure we have a valid integer ID
        try:
            version_id = int(version_id)
        except (ValueError, TypeError):
            print(f"Invalid version ID format: {version_id}")
            return Response({'error': f'Invalid version ID format: {version_id}'},
                           status=status.HTTP_400_BAD_REQUEST)
       
        # Get the policy version
        try:
            policy_version = PolicyVersion.objects.get(VersionId=version_id)
            print(f"Found policy version: {policy_version.VersionId} for policy {policy_version.PolicyId_id}")
        except PolicyVersion.DoesNotExist:
            print(f"Policy version with ID {version_id} not found")
            return Response({'error': f'Policy version with ID {version_id} not found'},
                           status=status.HTTP_404_NOT_FOUND)
       
        # Get the policy this version belongs to
        try:
            policy = Policy.objects.get(PolicyId=policy_version.PolicyId_id)
            print(f"Found policy: {policy.PolicyName} (ID: {policy.PolicyId})")
        except Policy.DoesNotExist:
            print(f"Policy with ID {policy_version.PolicyId_id} not found")
            return Response({'error': f'Policy with ID {policy_version.PolicyId_id} not found'},
                           status=status.HTTP_404_NOT_FOUND)
       
        # Get subpolicies for this policy
        subpolicies = SubPolicy.objects.filter(PolicyId=policy)
        print(f"Found {len(subpolicies)} subpolicies for policy {policy.PolicyId}")
       
        subpolicies_data = []
        for subpolicy in subpolicies:
            try:
                subpolicy_data = {
                    'id': subpolicy.SubPolicyId,
                    'name': subpolicy.SubPolicyName,
                    'category': policy.Department or 'General',
                    'status': subpolicy.Status or 'Unknown',
                    'description': subpolicy.Description or '',
                    'control': subpolicy.Control or '',
                    'identifier': subpolicy.Identifier,
                    'permanent_temporary': subpolicy.PermanentTemporary,
                    'policy_id': policy.PolicyId,
                    'policy_name': policy.PolicyName,
                    'created_by': subpolicy.CreatedByName,
                    'created_date': subpolicy.CreatedByDate
                }
                subpolicies_data.append(subpolicy_data)
                print(f"Added subpolicy: {subpolicy.SubPolicyId} - {subpolicy.SubPolicyName}")
            except Exception as e:
                print(f"Error processing subpolicy {subpolicy.SubPolicyId}: {str(e)}")
                # Continue to next subpolicy
       
        print(f"Returning {len(subpolicies_data)} subpolicies")
        return Response(subpolicies_data)
       
    except Exception as e:
        import traceback
        print(f"Error in all_policies_get_policy_version_subpolicies: {str(e)}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_subpolicy_compliances(request, subpolicy_id):
    """
    API endpoint to get all compliances for a specific subpolicy.
    """
    try:
        # Get the subpolicy
        subpolicy = get_object_or_404(SubPolicy, SubPolicyId=subpolicy_id)
        
        # Get compliances for this subpolicy
        compliances = Compliance.objects.filter(SubPolicy=subpolicy)
        
        compliances_data = []
        for compliance in compliances:
            compliance_data = {
                'ComplianceId': compliance.ComplianceId,
                'ComplianceItemDescription': compliance.ComplianceItemDescription,
                'Status': compliance.Status,
                'Criticality': compliance.Criticality,
                'MaturityLevel': compliance.MaturityLevel,
                'ActiveInactive': compliance.ActiveInactive,
                'ComplianceVersion': compliance.ComplianceVersion,
                'CreatedByName': compliance.CreatedByName,
                'CreatedByDate': compliance.CreatedByDate,
                'Identifier': compliance.Identifier,
                'IsRisk': compliance.IsRisk,
                'MandatoryOptional': compliance.MandatoryOptional,
                'ManualAutomatic': compliance.ManualAutomatic
            }
            compliances_data.append(compliance_data)
            
        return Response(compliances_data)
        
    except Exception as e:
        print(f"Error in all_policies_get_subpolicy_compliances: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def all_policies_get_compliance_versions(request, compliance_id):
    """
    API endpoint to get all versions of a specific compliance.
    """
    try:
        # Get the initial compliance
        compliance = get_object_or_404(Compliance, ComplianceId=compliance_id)
        
        # Initialize list to store all versions
        versions = []
        current = compliance
        
        # First, get all previous versions
        while current:
            versions.append(current)
            current = current.PreviousComplianceVersionId
            
        # Then, get all next versions
        current = compliance
        while True:
            next_versions = Compliance.objects.filter(PreviousComplianceVersionId=current.ComplianceId)
            if not next_versions.exists():
                break
            current = next_versions.first()
            versions.append(current)
            
        # Sort versions by version number
        versions.sort(key=lambda x: float(x.ComplianceVersion), reverse=True)
        
        # Convert to response format
        versions_data = []
        for version in versions:
            version_data = {
                'ComplianceId': version.ComplianceId,
                'ComplianceVersion': version.ComplianceVersion,
                'ComplianceItemDescription': version.ComplianceItemDescription,
                'Status': version.Status,
                'Criticality': version.Criticality,
                'MaturityLevel': version.MaturityLevel,
                'ActiveInactive': version.ActiveInactive,
                'CreatedByName': version.CreatedByName,
                'CreatedByDate': version.CreatedByDate.isoformat() if version.CreatedByDate else None,
                'Identifier': version.Identifier,
                'IsRisk': version.IsRisk,
                'MandatoryOptional': version.MandatoryOptional,
                'ManualAutomatic': version.ManualAutomatic,
                'PreviousVersionId': version.PreviousComplianceVersionId.ComplianceId if version.PreviousComplianceVersionId else None
            }
            versions_data.append(version_data)
            
        return Response(versions_data)
        
    except Exception as e:
        print(f"Error in all_policies_get_compliance_versions: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def export_data(request):
    try:
        data = request.data.get('data', [])
        file_format = request.data.get('file_format', 'xlsx')
        user_id = request.data.get('user_id', 'user123')
        options = request.data.get('options', {})

        # Call the export service
        result = export_service(data, file_format, user_id, options)

        # Get the file content from the result
        file_content = result.get('file_content', b'')
        file_name = result.get('file_name', f'export.{file_format}')

        # Set the content type based on file format
        content_types = {
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'pdf': 'application/pdf',
            'csv': 'text/csv',
            'json': 'application/json',
            'xml': 'application/xml',
            'txt': 'text/plain'
        }
        content_type = content_types.get(file_format, 'application/octet-stream')

        # Create the response with the file
        response = HttpResponse(file_content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        return response

    except Exception as e:
        print(f"Error in export_data: {str(e)}")
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def export_compliance_data(request):
    try:
        # Get all frameworks with their versions
        frameworks = Framework.objects.prefetch_related(
            'frameworkversion_set'
        ).all()

        export_data = []
        
        for framework in frameworks:
            # Get framework versions
            framework_versions = framework.frameworkversion_set.all()
            
            # Get policies for this framework
            policies = Policy.objects.filter(Framework=framework).prefetch_related(
                'policyversion_set'
            )
            
            for policy in policies:
                # Get policy versions
                policy_versions = policy.policyversion_set.all()
                
                # Get subpolicies for this policy
                subpolicies = SubPolicy.objects.filter(Policy=policy)
                
                for subpolicy in subpolicies:
                    # Get compliances for this subpolicy
                    compliances = Compliance.objects.filter(SubPolicy=subpolicy)
                    
                    for compliance in compliances:
                        # Create a row for each compliance
                        row = {
                            # Framework details
                            'framework_id': framework.FrameworkId,
                            'framework_name': framework.FrameworkName,
                            'framework_description': framework.FrameworkDescription,
                            'framework_category': framework.Category,
                            'framework_status': framework.ActiveInactive,
                            'framework_current_version': framework.CurrentVersion,
                            'framework_versions': [
                                {
                                    'version': v.Version,
                                    'created_by': v.CreatedBy,
                                    'created_date': v.CreatedDate.isoformat() if v.CreatedDate else None
                                } for v in framework_versions
                            ],
                            
                            # Policy details
                            'policy_id': policy.PolicyId,
                            'policy_name': policy.PolicyName,
                            'policy_description': policy.PolicyDescription,
                            'policy_department': policy.Department,
                            'policy_status': policy.Status,
                            'policy_active_inactive': policy.ActiveInactive,
                            'policy_current_version': policy.CurrentVersion,
                            'policy_versions': [
                                {
                                    'version': v.Version,
                                    'created_by': v.CreatedBy,
                                    'created_date': v.CreatedDate.isoformat() if v.CreatedDate else None
                                } for v in policy_versions
                            ],
                            
                            # Subpolicy details
                            'subpolicy_id': subpolicy.SubPolicyId,
                            'subpolicy_name': subpolicy.SubPolicyName,
                            'subpolicy_description': subpolicy.Description,
                            'subpolicy_status': subpolicy.Status,
                            'subpolicy_control': subpolicy.Control,
                            'subpolicy_identifier': subpolicy.Identifier,
                            
                            # Compliance details
                            'compliance_id': compliance.ComplianceId,
                            'compliance_description': compliance.ComplianceItemDescription,
                            'compliance_version': compliance.ComplianceVersion,
                            'compliance_status': compliance.Status,
                            'compliance_active_inactive': compliance.ActiveInactive,
                            'compliance_criticality': compliance.Criticality,
                            'compliance_maturity_level': compliance.MaturityLevel,
                            'compliance_mandatory_optional': compliance.MandatoryOptional,
                            'compliance_manual_automatic': compliance.ManualAutomatic,
                            'compliance_is_risk': compliance.IsRisk,
                            'compliance_possible_damage': compliance.PossibleDamage,
                            'compliance_mitigation': compliance.mitigation,
                            'compliance_impact': compliance.Impact,
                            'compliance_probability': compliance.Probability,
                            'compliance_created_by': compliance.CreatedByName,
                            'compliance_created_date': compliance.CreatedByDate.isoformat() if compliance.CreatedByDate else None,
                            'compliance_identifier': compliance.Identifier
                        }
                        export_data.append(row)

        # Get the requested format
        file_format = request.GET.get('format', 'xlsx')
        
        # Export the data using the export service
        result = export_service(
            data=export_data,
            file_format=file_format,
            user_id=request.GET.get('user_id', 'system'),
            options={
                'title': 'Compliance Export',
                'timestamp': datetime.datetime.now().isoformat()
            }
        )

        # Get the file content from the result
        file_content = result.get('file_content', result.get('file_buffer', b''))
        file_name = result.get('file_name', f'compliance_export_{datetime.datetime.now().strftime("%Y%m%d_%H%M%S")}.{file_format}')

        # Set content type based on format
        content_types = {
            'xlsx': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
            'pdf': 'application/pdf',
            'csv': 'text/csv',
            'json': 'application/json',
            'xml': 'application/xml',
            'txt': 'text/plain'
        }
        content_type = content_types.get(file_format, 'application/octet-stream')

        # Create response with file
        response = HttpResponse(file_content, content_type=content_type)
        response['Content-Disposition'] = f'attachment; filename="{file_name}"'
        
        return response

    except Exception as e:
        print(f"Error in export_compliance_data: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({
            'success': False,
            'message': str(e)
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@csrf_exempt
def download_export(request):
    try:
        # Parse the request data
        data = json.loads(request.body)
        export_format = data.get('format')
        
        # Prepare the data for export
        export_rows = []
        framework_base = {}
        policy_base = {}
        subpolicy_base = {}
        
        # Get framework data
        framework = data.get('framework', {})
        if framework:
            framework_base = {
                'Framework ID': framework.get('id'),
                'Framework Name': framework.get('name'),
                'Framework Description': framework.get('description'),
                'Framework Category': framework.get('category'),
                'Framework Status': framework.get('status')
            }
        
        # Get policy data
        policy = data.get('policy', {})
        if policy:
            policy_base = {
                'Policy ID': policy.get('id'),
                'Policy Name': policy.get('name'),
                'Policy Description': policy.get('description'),
                'Policy Department': policy.get('department'),
                'Policy Status': policy.get('status')
            }
            
        # Get subpolicy data
        subpolicy = data.get('subpolicy', {})
        if subpolicy:
            subpolicy_base = {
                'Subpolicy ID': subpolicy.get('id'),
                'Subpolicy Name': subpolicy.get('name'),
                'Subpolicy Description': subpolicy.get('description'),
                'Subpolicy Status': subpolicy.get('status')
            }
            
        # Get compliances and create rows
        compliances = data.get('compliances', [])
        for compliance in compliances:
            row = {
                **framework_base,
                **policy_base,
                **subpolicy_base,
                'Compliance ID': compliance.get('id'),
                'Compliance Description': compliance.get('description'),
                'Compliance Status': compliance.get('status'),
                'Maturity Level': compliance.get('maturityLevel'),
                'Mandatory/Optional': compliance.get('mandatoryOptional'),
                'Manual/Automatic': compliance.get('manualAutomatic'),
                'Criticality': compliance.get('category'),
                'Is Risk': compliance.get('isRisk'),
                'Created By': compliance.get('createdBy'),
                'Created Date': compliance.get('createdDate'),
                'Version': compliance.get('version'),
                'Identifier': compliance.get('identifier')
            }
            export_rows.append(row)
            
        # If no compliances, add a single row with framework/policy/subpolicy info
        if not export_rows and (framework or policy or subpolicy):
            row = {**framework_base}
            if policy:
                row.update(policy_base)
            if subpolicy:
                row.update(subpolicy_base)
            export_rows.append(row)
            
        # Convert to DataFrame for easy export
        df = pd.DataFrame(export_rows)
        
        # Export based on format
        if export_format == 'xlsx':
            output = BytesIO()
            df.to_excel(output, index=False, engine='openpyxl')
            output.seek(0)
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = 'attachment; filename=export.xlsx'
            return response
            
        elif export_format == 'csv':
            output = BytesIO()
            df.to_csv(output, index=False)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=export.csv'
            return response
            
        elif export_format == 'json':
            return HttpResponse(df.to_json(orient='records'), content_type='application/json')
            
        elif export_format == 'xml':
            output = df.to_xml(index=False)
            response = HttpResponse(output, content_type='application/xml')
            response['Content-Disposition'] = 'attachment; filename=export.xml'
            return response
            
        elif export_format == 'txt':
            output = BytesIO()
            df.to_string(output, index=False)
            output.seek(0)
            response = HttpResponse(output.read(), content_type='text/plain')
            response['Content-Disposition'] = 'attachment; filename=export.txt'
            return response
            
        else:
            return JsonResponse({'error': 'Unsupported export format'}, status=400)
            
    except Exception as e:
        print(f"Export error: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)
