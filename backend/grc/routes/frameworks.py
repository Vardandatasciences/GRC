from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from django.db import transaction
from django.db.models import Q
from django.utils import timezone
from ..models import Framework, FrameworkApproval, Policy, SubPolicy, PolicyApproval
import json
from datetime import datetime


@api_view(['POST'])
@permission_classes([AllowAny])
def create_framework_approval(request, framework_id):
    """
    Create a framework approval entry when a new framework is created
    """
    try:
        # Get the framework
        framework = Framework.objects.get(FrameworkId=framework_id)
        
        # Extract data for the approval
        user_id = request.data.get('UserId', 1)  # Default to 1 if not provided
        reviewer_id = framework.Reviewer if framework.Reviewer else request.data.get('ReviewerId', 2)  # Default to 2
        
        # Create extracted data JSON
        extracted_data = {
            "FrameworkName": framework.FrameworkName,
            "FrameworkDescription": framework.FrameworkDescription,
            "Category": framework.Category,
            "EffectiveDate": framework.EffectiveDate.isoformat() if framework.EffectiveDate else None,
            "StartDate": framework.StartDate.isoformat() if framework.StartDate else None,
            "EndDate": framework.EndDate.isoformat() if framework.EndDate else None,
            "CreatedByName": framework.CreatedByName,
            "Identifier": framework.Identifier,
            "Status": framework.Status,
            "ActiveInactive": framework.ActiveInactive,
            "type": "framework"
        }
        
        # Create the framework approval
        framework_approval = FrameworkApproval.objects.create(
            FrameworkId=framework,
            ExtractedData=extracted_data,
            UserId=user_id,
            ReviewerId=reviewer_id,
            Version="u1",  # Default initial version
            ApprovedNot=None  # Not yet approved
        )
        
        return Response({
            "message": "Framework approval created successfully",
            "ApprovalId": framework_approval.ApprovalId,
            "Version": framework_approval.Version
        }, status=status.HTTP_201_CREATED)
        
    except Framework.DoesNotExist:
        return Response({"error": "Framework not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_framework_approvals(request, framework_id=None):
    """
    Get all framework approvals or approvals for a specific framework
    """
    try:
        if framework_id:
            approvals = FrameworkApproval.objects.filter(FrameworkId=framework_id)
        else:
            approvals = FrameworkApproval.objects.all()
            
        approvals_data = []
        for approval in approvals:
            approval_data = {
                "ApprovalId": approval.ApprovalId,
                "FrameworkId": approval.FrameworkId.FrameworkId if approval.FrameworkId else None,
                "ExtractedData": approval.ExtractedData,
                "UserId": approval.UserId,
                "ReviewerId": approval.ReviewerId,
                "Version": approval.Version,
                "ApprovedNot": approval.ApprovedNot,
                "ApprovedDate": approval.ApprovedDate.isoformat() if approval.ApprovedDate else None
            }
            
            # If this is an approved framework, also include its policies
            if approval.ApprovedNot is True:
                policies = Policy.objects.filter(FrameworkId=approval.FrameworkId)
                policies_data = []
                
                for policy in policies:
                    policy_data = {
                        "PolicyId": policy.PolicyId,
                        "PolicyName": policy.PolicyName,
                        "Status": policy.Status
                    }
                    policies_data.append(policy_data)
                
                approval_data["policies"] = policies_data
            
            approvals_data.append(approval_data)
            
        return Response(approvals_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_framework_approval(request, approval_id):
    """
    Update a framework approval status
    """
    try:
        approval = FrameworkApproval.objects.get(ApprovalId=approval_id)
        
        # Update approval status
        approved = request.data.get('ApprovedNot')
        if approved is not None:
            approval.ApprovedNot = approved
            
            # If approved, set approval date
            if approved:
                approval.ApprovedDate = timezone.now().date()
                
                # Also update the framework status
                if approval.FrameworkId:
                    framework = approval.FrameworkId
                    framework.Status = 'Approved'
                    framework.save()
            elif approved is False:
                # If rejected, update framework status
                if approval.FrameworkId:
                    framework = approval.FrameworkId
                    framework.Status = 'Rejected'
                    framework.save()
        
        # Update extracted data if provided
        extracted_data = request.data.get('ExtractedData')
        if extracted_data:
            approval.ExtractedData = extracted_data
            
        approval.save()
        
        return Response({
            "message": "Framework approval updated successfully",
            "ApprovalId": approval.ApprovalId,
            "ApprovedNot": approval.ApprovedNot,
            "ApprovedDate": approval.ApprovedDate.isoformat() if approval.ApprovedDate else None
        }, status=status.HTTP_200_OK)
        
    except FrameworkApproval.DoesNotExist:
        return Response({"error": "Framework approval not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_framework_review(request, framework_id):
    """
    Submit a review for a framework
    """
    try:
        framework = Framework.objects.get(FrameworkId=framework_id)
        
        # Get current version info
        current_version = request.data.get('currentVersion', 'u1')
        user_id = request.data.get('UserId', 1)
        reviewer_id = request.data.get('ReviewerId', 2)
        approved = request.data.get('ApprovedNot')
        extracted_data = request.data.get('ExtractedData')
        
        # Create or update the framework approval
        with transaction.atomic():
            # Determine the next version
            # Check if there's already a reviewer version for this framework
            latest_reviewer_version = FrameworkApproval.objects.filter(
                FrameworkId=framework,
                Version__startswith='r'
            ).order_by('-ApprovalId').first()
            
            if latest_reviewer_version:
                # Increment the existing reviewer version
                try:
                    version_num = int(latest_reviewer_version.Version[1:])
                    new_version = f'r{version_num + 1}'
                except ValueError:
                    new_version = 'r1'
            else:
                # First reviewer version
                new_version = 'r1'
            
            # Create a new approval record with the reviewer version
            new_approval = FrameworkApproval.objects.create(
                FrameworkId=framework,
                ExtractedData=extracted_data,
                UserId=user_id,
                ReviewerId=reviewer_id,
                Version=new_version,
                ApprovedNot=approved
            )
            
            # Set approval date if approved
            if approved:
                new_approval.ApprovedDate = timezone.now().date()
                
                # Update framework status
                framework.Status = 'Approved'
                framework.save()
            elif approved is False:
                # Update framework status if rejected
                framework.Status = 'Rejected'
                framework.save()
                
                # Also reject all policies in this framework
                # Get all policies for this framework
                policies = Policy.objects.filter(FrameworkId=framework)
                
                for policy in policies:
                    # Update policy status to rejected
                    policy.Status = 'Rejected'
                    policy.save()
                    
                    # Create rejection entry in policy approval
                    policy_extracted_data = {
                        "PolicyName": policy.PolicyName,
                        "PolicyDescription": policy.PolicyDescription,
                        "Status": "Rejected",
                        "Scope": policy.Scope,
                        "Objective": policy.Objective,
                        "type": "policy",
                        "framework_rejection": True,
                        "rejection_reason": "Framework was rejected"
                    }
                    
                    # Get all subpolicies for this policy
                    subpolicies = SubPolicy.objects.filter(PolicyId=policy)
                    
                    # Create subpolicies data
                    subpolicies_data = []
                    for subpolicy in subpolicies:
                        # Update subpolicy status to rejected
                        subpolicy.Status = 'Rejected'
                        subpolicy.save()
                        
                        subpolicy_data = {
                            "SubPolicyId": subpolicy.SubPolicyId,
                            "SubPolicyName": subpolicy.SubPolicyName,
                            "Identifier": subpolicy.Identifier,
                            "Description": subpolicy.Description,
                            "Status": "Rejected",
                            "approval": {
                                "approved": False,
                                "remarks": "Framework was rejected"
                            }
                        }
                        subpolicies_data.append(subpolicy_data)
                    
                    # Add subpolicies to policy data
                    policy_extracted_data["subpolicies"] = subpolicies_data
                    
                    # Create policy approval record
                    PolicyApproval.objects.create(
                        PolicyId=policy,
                        ExtractedData=policy_extracted_data,
                        UserId=user_id,
                        ReviewerId=reviewer_id,
                        Version="r1",  # Reviewer rejected directly
                        ApprovedNot=False  # Rejected
                    )
            
            return Response({
                "message": "Framework review submitted successfully",
                "ApprovalId": new_approval.ApprovalId,
                "Version": new_approval.Version,
                "ApprovedNot": new_approval.ApprovedNot,
                "ApprovedDate": new_approval.ApprovedDate.isoformat() if new_approval.ApprovedDate else None
            }, status=status.HTTP_200_OK)
            
    except Framework.DoesNotExist:
        return Response({"error": "Framework not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_latest_framework_approval(request, framework_id):
    """
    Get the latest approval for a framework
    """
    try:
        # Get the latest approval by created date
        latest_approval = FrameworkApproval.objects.filter(
            FrameworkId=framework_id
        ).order_by('-ApprovalId').first()
        
        if not latest_approval:
            return Response({"message": "No approvals found for this framework"}, status=status.HTTP_404_NOT_FOUND)
        
        approval_data = {
            "ApprovalId": latest_approval.ApprovalId,
            "FrameworkId": latest_approval.FrameworkId.FrameworkId if latest_approval.FrameworkId else None,
            "ExtractedData": latest_approval.ExtractedData,
            "UserId": latest_approval.UserId,
            "ReviewerId": latest_approval.ReviewerId,
            "Version": latest_approval.Version,
            "ApprovedNot": latest_approval.ApprovedNot,
            "ApprovedDate": latest_approval.ApprovedDate.isoformat() if latest_approval.ApprovedDate else None
        }
        
        return Response(approval_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['PUT'])
@permission_classes([AllowAny])
def resubmit_framework(request, framework_id):
    """
    Resubmit a rejected framework for review
    """
    try:
        framework = Framework.objects.get(FrameworkId=framework_id)
        
        # Check if framework is rejected
        if framework.Status != 'Rejected':
            return Response({"error": "Only rejected frameworks can be resubmitted"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Update framework data from request
        for field in ['FrameworkName', 'FrameworkDescription', 'Category', 'Identifier']:
            if field in request.data:
                setattr(framework, field, request.data[field])
        
        # Update dates if provided
        for date_field in ['EffectiveDate', 'StartDate', 'EndDate']:
            if date_field in request.data and request.data[date_field]:
                try:
                    date_value = datetime.strptime(request.data[date_field], '%Y-%m-%d').date()
                    setattr(framework, date_field, date_value)
                except ValueError:
                    pass
        
        # Change status back to Under Review
        framework.Status = 'Under Review'
        framework.save()
        
        # Create a new framework approval for the resubmission
        with transaction.atomic():
            # Get the latest version
            latest_approval = FrameworkApproval.objects.filter(
                FrameworkId=framework
            ).order_by('-ApprovalId').first()
            
            current_version = latest_approval.Version if latest_approval else 'u1'
            
            # For user resubmissions, version should be u2, u3, etc.
            if current_version.startswith('r'):
                # Get the latest user version
                latest_user_version = FrameworkApproval.objects.filter(
                    FrameworkId=framework,
                    Version__startswith='u'
                ).order_by('-ApprovalId').first()
                
                if latest_user_version:
                    try:
                        version_num = int(latest_user_version.Version[1:])
                        new_version = f'u{version_num + 1}'
                    except ValueError:
                        new_version = 'u2'
                else:
                    new_version = 'u2'
            elif current_version.startswith('u'):
                # Increment user version
                try:
                    version_num = int(current_version[1:])
                    new_version = f'u{version_num + 1}'
                except ValueError:
                    new_version = 'u2'
            else:
                new_version = 'u2'  # Default if version format is unexpected
            
            # Create extracted data for new approval
            extracted_data = {
                "FrameworkName": framework.FrameworkName,
                "FrameworkDescription": framework.FrameworkDescription,
                "Category": framework.Category,
                "EffectiveDate": framework.EffectiveDate.isoformat() if framework.EffectiveDate else None,
                "StartDate": framework.StartDate.isoformat() if framework.StartDate else None,
                "EndDate": framework.EndDate.isoformat() if framework.EndDate else None,
                "CreatedByName": framework.CreatedByName,
                "Identifier": framework.Identifier,
                "Status": framework.Status,
                "ActiveInactive": framework.ActiveInactive,
                "type": "framework",
                "resubmitted": True,
                "previousVersion": latest_approval.ExtractedData if latest_approval else None
            }
            
            # Create new approval
            new_approval = FrameworkApproval.objects.create(
                FrameworkId=framework,
                ExtractedData=extracted_data,
                UserId=latest_approval.UserId if latest_approval else 1,
                ReviewerId=latest_approval.ReviewerId if latest_approval else 2,
                Version=new_version,
                ApprovedNot=None  # Reset approval status
            )
            
            return Response({
                "message": "Framework resubmitted successfully",
                "ApprovalId": new_approval.ApprovalId,
                "Version": new_approval.Version
            }, status=status.HTTP_200_OK)
        
    except Framework.DoesNotExist:
        return Response({"error": "Framework not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 