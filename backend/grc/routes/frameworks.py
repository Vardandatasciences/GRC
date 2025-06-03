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
        
        print(f"[DEBUG] Processing framework review for framework ID: {framework_id}")
        print(f"[DEBUG] Current framework status: {framework.Status}")
        print(f"[DEBUG] Approval decision: {'Approved' if approved is True else 'Rejected' if approved is False else 'Under Review'}")
        
        if not extracted_data:
            return Response({'error': 'ExtractedData is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure proper status values in JSON data
        if approved is True or approved == 1:
            # Framework is approved
            extracted_data['Status'] = 'Approved'
            if 'framework_approval' not in extracted_data:
                extracted_data['framework_approval'] = {}
            extracted_data['framework_approval']['approved'] = True
            extracted_data['framework_approval']['remarks'] = ''
            approved = 1  # Ensure it's stored as 1
        elif approved is False or approved == 0:
            # Framework is rejected
            extracted_data['Status'] = 'Rejected'
            if 'framework_approval' not in extracted_data:
                extracted_data['framework_approval'] = {}
            extracted_data['framework_approval']['approved'] = False
            # Keep existing remarks if any
            if 'remarks' not in extracted_data['framework_approval']:
                extracted_data['framework_approval']['remarks'] = request.data.get('remarks', '')
            approved = 0  # Ensure it's stored as 0
        else:
            # Still under review
            extracted_data['Status'] = 'Under Review'
            if 'framework_approval' not in extracted_data:
                extracted_data['framework_approval'] = {}
            extracted_data['framework_approval']['approved'] = None
            approved = None
        
        # Create or update the framework approval
        with transaction.atomic():
            # Determine the next version
            # Check if there's already a reviewer version for this framework
            latest_reviewer_version = FrameworkApproval.objects.filter(
                FrameworkId=framework,
                Version__startswith='R'
            ).order_by('-ApprovalId').first()
            
            if latest_reviewer_version:
                # Increment the existing reviewer version
                try:
                    version_num = int(latest_reviewer_version.Version[1:])
                    new_version = f'R{version_num + 1}'
                except ValueError:
                    new_version = 'R1'
            else:
                # First reviewer version
                new_version = 'R1'
            
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
            if approved == 1 or approved is True:
                new_approval.ApprovedDate = timezone.now().date()
                new_approval.save()
                
                # Update framework status
                framework.Status = 'Approved'
                framework.ActiveInactive = 'Active'
                framework.save()
                
                print(f"[DEBUG] Framework {framework_id} approved and set to Active")
                
            elif approved == 0 or approved is False:
                # Update framework status if rejected
                framework.Status = 'Rejected'
                framework.ActiveInactive = 'Inactive'
                framework.save()
                
                print(f"[DEBUG] Framework {framework_id} rejected and set to Inactive")
                
                # Also reject all policies in this framework
                # Get all policies for this framework
                policies = Policy.objects.filter(FrameworkId=framework)
                
                print(f"[DEBUG] Found {policies.count()} policies to reject in framework {framework_id}")
                
                for policy in policies:
                    # Update policy status to rejected
                    policy.Status = 'Rejected'
                    policy.ActiveInactive = 'Inactive'
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
                        Version="R1",  # Reviewer rejected directly
                        ApprovedNot=0  # Rejected
                    )
                    
                    print(f"[DEBUG] Policy {policy.PolicyId} rejected due to framework rejection")
            else:
                # Framework still under review
                framework.Status = 'Under Review'
                framework.save()
                
                print(f"[DEBUG] Framework {framework_id} set to Under Review")
            
            return Response({
                "message": "Framework review submitted successfully",
                "FrameworkId": framework_id,
                "ApprovalId": new_approval.ApprovalId,
                "Version": new_approval.Version,
                "Status": framework.Status,
                "ApprovedNot": new_approval.ApprovedNot,
                "ApprovedDate": new_approval.ApprovedDate.isoformat() if new_approval.ApprovedDate else None
            }, status=status.HTTP_200_OK)
            
    except Framework.DoesNotExist:
        return Response({"error": "Framework not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error submitting framework review: {str(e)}")
        import traceback
        traceback.print_exc()
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

@api_view(['PUT'])
@permission_classes([AllowAny])
def submit_framework_approval_review(request, framework_id):
    """
    Submit a review for a framework (approve/reject)
    """
    try:
        framework = Framework.objects.get(FrameworkId=framework_id)
        
        # Get data from request
        extracted_data = request.data.get('ExtractedData')
        approved_not = request.data.get('ApprovedNot')
        reviewer_id = request.data.get('ReviewerId', 2)
        user_id = request.data.get('UserId', 1)
        remarks = request.data.get('remarks', '')
        
        print(f"[DEBUG] Processing framework approval review for framework ID: {framework_id}")
        print(f"[DEBUG] Current framework status: {framework.Status}")
        print(f"[DEBUG] Approval decision: {'Approved' if approved_not is True else 'Rejected' if approved_not is False else 'Under Review'}")
        
        if not extracted_data:
            return Response({'error': 'ExtractedData is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Ensure proper status values in JSON data
        if approved_not is True or approved_not == 1:
            # Framework is approved
            extracted_data['Status'] = 'Approved'
            if 'framework_approval' not in extracted_data:
                extracted_data['framework_approval'] = {}
            extracted_data['framework_approval']['approved'] = True
            extracted_data['framework_approval']['remarks'] = ''
            approved_not = 1  # Ensure it's stored as 1
        elif approved_not is False or approved_not == 0:
            # Framework is rejected
            extracted_data['Status'] = 'Rejected'
            if 'framework_approval' not in extracted_data:
                extracted_data['framework_approval'] = {}
            extracted_data['framework_approval']['approved'] = False
            extracted_data['framework_approval']['remarks'] = remarks
            approved_not = 0  # Ensure it's stored as 0
        
        # Get all versions for this framework
        framework_approvals = FrameworkApproval.objects.filter(
            FrameworkId=framework_id
        ).order_by('-Version')
        
        # Initialize version
        new_version = 'R1'  # Default first reviewer version
        
        if framework_approvals:
            # Use list comprehension to get version types
            r_versions = [fa.Version for fa in framework_approvals if fa.Version and fa.Version.startswith('R')]
            u_versions = [fa.Version for fa in framework_approvals if fa.Version and fa.Version.startswith('u')]
            
            print(f"[DEBUG] Existing R versions: {r_versions}")
            print(f"[DEBUG] Existing u versions: {u_versions}")
            
            if r_versions:
                # Get the highest R version number
                latest_r_num = max([int(v[1:]) for v in r_versions if v[1:].isdigit()])
                new_version = f'R{latest_r_num + 1}'
            else:
                new_version = 'R1'
            print(f"[DEBUG] Selected version: {new_version}")
        
        # Verify this version doesn't already exist
        existing_versions = [fa.Version for fa in framework_approvals]
        while new_version in existing_versions:
            # If version exists, increment the number
            prefix = new_version[0]
            num = int(new_version[1:]) + 1
            new_version = f'{prefix}{num}'
            print(f"[DEBUG] Incrementing version to: {new_version}")
        
        # Set approved date if framework is approved
        approved_date = timezone.now().date() if approved_not == 1 or approved_not is True else None
        
        # Create new framework approval with incremented version
        new_approval = FrameworkApproval.objects.create(
            FrameworkId=framework,
            ExtractedData=extracted_data,
            UserId=user_id,
            ReviewerId=reviewer_id,
            ApprovedNot=approved_not,
            ApprovedDate=approved_date,
            Version=new_version
        )
        print(f"[DEBUG] Created new framework approval with ID: {new_approval.ApprovalId}, Version: {new_version}")
        
        # Update framework status
        old_status = framework.Status
        if approved_not == 1 or approved_not is True:
            framework.Status = 'Approved'
            framework.ActiveInactive = 'Active'
        elif approved_not == 0 or approved_not is False:
            framework.Status = 'Rejected'
            framework.ActiveInactive = 'Inactive'
            
            # Also reject all policies and subpolicies in this framework
            policies = Policy.objects.filter(FrameworkId=framework)
            for policy in policies:
                policy.Status = 'Rejected'
                policy.ActiveInactive = 'Inactive'
                policy.save()
                
                # Reject all subpolicies
                SubPolicy.objects.filter(PolicyId=policy).update(Status='Rejected')
        else:
            framework.Status = 'Under Review'
        
        framework.save()
        print(f"[DEBUG] Updated framework status from {old_status} to {framework.Status}")
        
        return Response({
            'message': 'Framework review submitted successfully',
            'FrameworkId': framework_id,
            'ApprovalId': new_approval.ApprovalId,
            'Version': new_version,
            'Status': framework.Status,
            'ApprovedNot': approved_not,
            'ApprovedDate': approved_date.isoformat() if approved_date else None
        }, status=status.HTTP_201_CREATED)
    
    except Framework.DoesNotExist:
        return Response({'error': 'Framework not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error submitting framework review: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['PUT'])
@permission_classes([AllowAny])
def resubmit_framework_approval(request, approval_id):
    """
    Resubmit a rejected framework for review
    """
    try:
        approval = FrameworkApproval.objects.get(ApprovalId=approval_id)
        framework = approval.FrameworkId
        
        if not framework:
            return Response({'error': 'Framework not found'}, status=status.HTTP_404_NOT_FOUND)
        
        print(f"[DEBUG] Resubmitting framework approval {approval_id} for framework {framework.FrameworkId}")
        
        # Get updated data from request
        data = request.data.copy()
        updated_extracted_data = data.get('ExtractedData')
        
        if updated_extracted_data:
            print(f"[DEBUG] Received updated ExtractedData with {len(updated_extracted_data.get('policies', []))} policies")
            
            # Update framework fields in the database if provided
            framework_updates = {}
            if 'FrameworkName' in updated_extracted_data:
                framework_updates['FrameworkName'] = updated_extracted_data['FrameworkName']
            if 'FrameworkDescription' in updated_extracted_data:
                framework_updates['FrameworkDescription'] = updated_extracted_data['FrameworkDescription']
            if 'Category' in updated_extracted_data:
                framework_updates['Category'] = updated_extracted_data['Category']
            if 'EffectiveDate' in updated_extracted_data:
                try:
                    framework_updates['EffectiveDate'] = datetime.strptime(updated_extracted_data['EffectiveDate'], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    pass
            if 'StartDate' in updated_extracted_data:
                try:
                    framework_updates['StartDate'] = datetime.strptime(updated_extracted_data['StartDate'], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    pass
            if 'EndDate' in updated_extracted_data:
                try:
                    framework_updates['EndDate'] = datetime.strptime(updated_extracted_data['EndDate'], '%Y-%m-%d').date()
                except (ValueError, TypeError):
                    pass
            
            # Update framework in database
            if framework_updates:
                for field, value in framework_updates.items():
                    setattr(framework, field, value)
                print(f"[DEBUG] Updated framework fields: {list(framework_updates.keys())}")
            
            # Update policies and subpolicies in database if provided
            if 'policies' in updated_extracted_data:
                for policy_data in updated_extracted_data['policies']:
                    try:
                        policy_id = policy_data.get('PolicyId')
                        if policy_id:
                            policy = Policy.objects.get(PolicyId=policy_id, FrameworkId=framework)
                            
                            # Update policy fields
                            policy_updates = {}
                            if 'PolicyName' in policy_data:
                                policy_updates['PolicyName'] = policy_data['PolicyName']
                            if 'PolicyDescription' in policy_data:
                                policy_updates['PolicyDescription'] = policy_data['PolicyDescription']
                            if 'Scope' in policy_data:
                                policy_updates['Scope'] = policy_data['Scope']
                            if 'Objective' in policy_data:
                                policy_updates['Objective'] = policy_data['Objective']
                            if 'Department' in policy_data:
                                policy_updates['Department'] = policy_data['Department']
                            if 'Identifier' in policy_data:
                                policy_updates['Identifier'] = policy_data['Identifier']
                            if 'Applicability' in policy_data:
                                policy_updates['Applicability'] = policy_data['Applicability']
                            
                            # Update policy in database
                            if policy_updates:
                                for field, value in policy_updates.items():
                                    setattr(policy, field, value)
                                print(f"[DEBUG] Updated policy {policy_id} fields: {list(policy_updates.keys())}")
                            
                            # Reset policy status to Under Review if it was rejected
                            if policy.Status == 'Rejected':
                                policy.Status = 'Under Review'
                                policy_data['Status'] = 'Under Review'
                                print(f"[DEBUG] Reset policy {policy_id} status to Under Review")
                            
                            policy.save()
                            
                            # Update subpolicies
                            if 'subpolicies' in policy_data:
                                for subpolicy_data in policy_data['subpolicies']:
                                    try:
                                        subpolicy_id = subpolicy_data.get('SubPolicyId')
                                        if subpolicy_id:
                                            subpolicy = SubPolicy.objects.get(SubPolicyId=subpolicy_id, PolicyId=policy)
                                            
                                            # Update subpolicy fields
                                            subpolicy_updates = {}
                                            if 'SubPolicyName' in subpolicy_data:
                                                subpolicy_updates['SubPolicyName'] = subpolicy_data['SubPolicyName']
                                            if 'Description' in subpolicy_data:
                                                subpolicy_updates['Description'] = subpolicy_data['Description']
                                            if 'Control' in subpolicy_data:
                                                subpolicy_updates['Control'] = subpolicy_data['Control']
                                            if 'Identifier' in subpolicy_data:
                                                subpolicy_updates['Identifier'] = subpolicy_data['Identifier']
                                            
                                            # Update subpolicy in database
                                            if subpolicy_updates:
                                                for field, value in subpolicy_updates.items():
                                                    setattr(subpolicy, field, value)
                                                print(f"[DEBUG] Updated subpolicy {subpolicy_id} fields: {list(subpolicy_updates.keys())}")
                                            
                                            # Reset subpolicy status to Under Review if it was rejected
                                            if subpolicy.Status == 'Rejected':
                                                subpolicy.Status = 'Under Review'
                                                subpolicy_data['Status'] = 'Under Review'
                                                print(f"[DEBUG] Reset subpolicy {subpolicy_id} status to Under Review")
                                            
                                            subpolicy.save()
                                            
                                    except SubPolicy.DoesNotExist:
                                        print(f"[DEBUG] Subpolicy {subpolicy_id} not found, skipping")
                                        continue
                                    except Exception as e:
                                        print(f"[DEBUG] Error updating subpolicy {subpolicy_id}: {str(e)}")
                                        continue
                            
                    except Policy.DoesNotExist:
                        print(f"[DEBUG] Policy {policy_id} not found, skipping")
                        continue
                    except Exception as e:
                        print(f"[DEBUG] Error updating policy {policy_id}: {str(e)}")
                        continue
        
        # Get all versions for this framework to find the latest u version
        framework_approvals = FrameworkApproval.objects.filter(
            FrameworkId=framework
        ).order_by('-Version')
        
        # Find the latest u version
        u_versions = [fa.Version for fa in framework_approvals if fa.Version and fa.Version.startswith('u')]
        new_version = 'u1'
        
        if u_versions:
            # Get the highest u version number
            latest_u_num = max([int(v[1:]) for v in u_versions if v[1:].isdigit()])
            new_version = f'u{latest_u_num + 1}'
        
        print(f"[DEBUG] New version will be: {new_version}")
        
        # Set framework status back to Under Review
        framework.Status = 'Under Review'
        framework.save()
        
        # Prepare the updated extracted data for the new approval
        if updated_extracted_data:
            # Ensure the extracted data has the updated framework info
            final_extracted_data = updated_extracted_data.copy()
            final_extracted_data.update({
                'FrameworkId': framework.FrameworkId,
                'FrameworkName': framework.FrameworkName,
                'FrameworkDescription': framework.FrameworkDescription,
                'Category': framework.Category,
                'EffectiveDate': framework.EffectiveDate.isoformat() if framework.EffectiveDate else None,
                'StartDate': framework.StartDate.isoformat() if framework.StartDate else None,
                'EndDate': framework.EndDate.isoformat() if framework.EndDate else None,
                'CreatedByName': framework.CreatedByName,
                'Identifier': framework.Identifier,
                'Status': 'Under Review',
                'ActiveInactive': framework.ActiveInactive,
                'type': 'framework'
            })
            
            # Reset approval status in extracted data
            if 'approval' in final_extracted_data:
                final_extracted_data['approval']['approved'] = None
                final_extracted_data['approval']['remarks'] = ''
            if 'framework_approval' in final_extracted_data:
                final_extracted_data['framework_approval']['approved'] = None
                final_extracted_data['framework_approval']['remarks'] = ''
        else:
            # Fallback: create basic extracted data
            final_extracted_data = {
                'FrameworkId': framework.FrameworkId,
                'FrameworkName': framework.FrameworkName,
                'FrameworkDescription': framework.FrameworkDescription,
                'Category': framework.Category,
                'EffectiveDate': framework.EffectiveDate.isoformat() if framework.EffectiveDate else None,
                'StartDate': framework.StartDate.isoformat() if framework.StartDate else None,
                'EndDate': framework.EndDate.isoformat() if framework.EndDate else None,
                'CreatedByName': framework.CreatedByName,
                'Identifier': framework.Identifier,
                'Status': 'Under Review',
                'ActiveInactive': framework.ActiveInactive,
                'type': 'framework'
            }
        
        # Create new framework approval with incremented u version
        new_approval = FrameworkApproval.objects.create(
            FrameworkId=framework,
            ExtractedData=final_extracted_data,
            UserId=approval.UserId,
            ReviewerId=approval.ReviewerId,
            ApprovedNot=None,
            Version=new_version
        )
        
        print(f"[DEBUG] Created new framework approval {new_approval.ApprovalId} with version {new_version}")
        print(f"[DEBUG] ExtractedData contains {len(final_extracted_data.get('policies', []))} policies")
        
        return Response({
            'message': 'Framework resubmitted successfully',
            'FrameworkId': framework.FrameworkId,
            'ApprovalId': new_approval.ApprovalId,
            'Status': 'Under Review',
            'version': new_version
        }, status=status.HTTP_200_OK)
        
    except FrameworkApproval.DoesNotExist:
        return Response({'error': 'Framework approval not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error resubmitting framework approval: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_framework_for_approval(request, framework_id):
    """
    Get framework details with all policies and subpolicies for approval process
    """
    try:
        print(f"[DEBUG] Getting framework for approval - Framework ID: {framework_id}")
        framework = Framework.objects.get(FrameworkId=framework_id)
        print(f"[DEBUG] Found framework: {framework.FrameworkName}")
        
        # Get the latest framework approval
        latest_framework_approval = FrameworkApproval.objects.filter(
            FrameworkId=framework
        ).order_by('-ApprovalId').first()
        print(f"[DEBUG] Latest framework approval found: {latest_framework_approval is not None}")
        
        # Get all policies in this framework
        policies = Policy.objects.filter(FrameworkId=framework)
        print(f"[DEBUG] Found {policies.count()} policies in framework")
        
        policies_data = []
        for policy in policies:
            print(f"[DEBUG] Processing policy: {policy.PolicyName} (ID: {policy.PolicyId})")
            
            # Get the latest policy approval
            latest_policy_approval = PolicyApproval.objects.filter(
                PolicyId=policy
            ).order_by('-ApprovalId').first()
            
            # Get all subpolicies for this policy
            subpolicies = SubPolicy.objects.filter(PolicyId=policy)
            print(f"[DEBUG] Found {subpolicies.count()} subpolicies for policy {policy.PolicyId}")
            subpolicies_data = []
            
            for subpolicy in subpolicies:
                print(f"[DEBUG] Processing subpolicy: {subpolicy.SubPolicyName} (ID: {subpolicy.SubPolicyId})")
                subpolicy_data = {
                    "SubPolicyId": subpolicy.SubPolicyId,
                    "SubPolicyName": subpolicy.SubPolicyName,
                    "Identifier": subpolicy.Identifier,
                    "Description": subpolicy.Description,
                    "Status": subpolicy.Status,
                    "Control": subpolicy.Control,
                    "CreatedByName": subpolicy.CreatedByName,
                    "CreatedByDate": subpolicy.CreatedByDate.isoformat() if subpolicy.CreatedByDate else None,
                    "PermanentTemporary": subpolicy.PermanentTemporary,
                    "approval": {
                        "approved": True if subpolicy.Status == 'Approved' else False if subpolicy.Status == 'Rejected' else None,
                        "remarks": ""
                    },
                    "version": "u1"  # Default version
                }
                subpolicies_data.append(subpolicy_data)
            
            policy_data = {
                "PolicyId": policy.PolicyId,
                "PolicyName": policy.PolicyName,
                "PolicyDescription": policy.PolicyDescription,
                "Status": policy.Status,
                "Scope": policy.Scope,
                "Objective": policy.Objective,
                "Department": policy.Department,
                "StartDate": policy.StartDate.isoformat() if policy.StartDate else None,
                "EndDate": policy.EndDate.isoformat() if policy.EndDate else None,
                "Identifier": policy.Identifier,
                "CreatedByName": policy.CreatedByName,
                "CreatedByDate": policy.CreatedByDate.isoformat() if policy.CreatedByDate else None,
                "Applicability": policy.Applicability,
                "PermanentTemporary": policy.PermanentTemporary,
                "subpolicies": subpolicies_data,
                "approval": {
                    "approved": True if policy.Status == 'Approved' else False if policy.Status == 'Rejected' else None,
                    "remarks": ""
                },
                "version": latest_policy_approval.Version if latest_policy_approval else "u1",
                "type": "policy"
            }
            policies_data.append(policy_data)
        
        print(f"[DEBUG] Total policies processed: {len(policies_data)}")
        
        # Create framework data
        framework_data = {
            "FrameworkId": framework.FrameworkId,
            "FrameworkName": framework.FrameworkName,
            "FrameworkDescription": framework.FrameworkDescription,
            "Category": framework.Category,
            "EffectiveDate": framework.EffectiveDate.isoformat() if framework.EffectiveDate else None,
            "StartDate": framework.StartDate.isoformat() if framework.StartDate else None,
            "EndDate": framework.EndDate.isoformat() if framework.EndDate else None,
            "CreatedByName": framework.CreatedByName,
            "CreatedByDate": framework.CreatedByDate.isoformat() if framework.CreatedByDate else None,
            "Identifier": framework.Identifier,
            "Status": framework.Status,
            "ActiveInactive": framework.ActiveInactive,
            "policies": policies_data,
            "type": "framework",
            "approval": {
                "approved": True if framework.Status == 'Approved' else False if framework.Status == 'Rejected' else None,
                "remarks": ""
            }
        }
        
        print(f"[DEBUG] Framework data created with {len(framework_data['policies'])} policies")
        
        # If we have a framework approval, use its data
        if latest_framework_approval:
            approval_data = {
                "ApprovalId": latest_framework_approval.ApprovalId,
                "FrameworkId": framework.FrameworkId,
                "ExtractedData": framework_data,
                "UserId": latest_framework_approval.UserId,
                "ReviewerId": latest_framework_approval.ReviewerId,
                "Version": latest_framework_approval.Version,
                "ApprovedNot": latest_framework_approval.ApprovedNot,
                "ApprovedDate": latest_framework_approval.ApprovedDate.isoformat() if latest_framework_approval.ApprovedDate else None
            }
        else:
            # Create a basic approval structure
            approval_data = {
                "ApprovalId": None,
                "FrameworkId": framework.FrameworkId,
                "ExtractedData": framework_data,
                "UserId": 1,  # Default user
                "ReviewerId": 2,  # Default reviewer
                "Version": "u1",
                "ApprovedNot": None,
                "ApprovedDate": None
            }
        
        print(f"[DEBUG] Returning approval data with ExtractedData containing {len(approval_data['ExtractedData']['policies'])} policies")
        return Response(approval_data, status=status.HTTP_200_OK)
        
    except Framework.DoesNotExist:
        print(f"[DEBUG] Framework with ID {framework_id} not found")
        return Response({"error": "Framework not found"}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error getting framework for approval: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['PUT'])
@permission_classes([AllowAny])
def approve_framework_policy(request, framework_id, policy_id):
    """
    Approve a policy within a framework
    """
    try:
        framework = Framework.objects.get(FrameworkId=framework_id)
        policy = Policy.objects.get(PolicyId=policy_id, FrameworkId=framework)
        
        # Update policy status
        policy.Status = 'Approved'
        policy.save()
        
        # Check if all subpolicies of this policy are approved
        all_subpolicies = SubPolicy.objects.filter(PolicyId=policy)
        all_subpolicies_approved = all(sub.Status == 'Approved' for sub in all_subpolicies)
        
        if not all_subpolicies_approved:
            return Response({
                'error': 'Cannot approve policy until all subpolicies are approved',
                'PolicyId': policy_id,
                'Status': policy.Status
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Check if all policies in the framework are now approved
        all_framework_policies = Policy.objects.filter(FrameworkId=framework)
        all_policies_approved = all(pol.Status == 'Approved' for pol in all_framework_policies)
        
        response_data = {
            'message': 'Policy approved successfully',
            'PolicyId': policy_id,
            'Status': policy.Status,
            'FrameworkUpdated': False
        }
        
        if all_policies_approved:
            # Automatically approve the framework
            framework.Status = 'Approved'
            framework.ActiveInactive = 'Active'
            framework.save()
            
            response_data['FrameworkUpdated'] = True
            response_data['FrameworkStatus'] = 'Approved'
            response_data['message'] = 'Policy approved and framework automatically approved'
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Framework.DoesNotExist:
        return Response({'error': 'Framework not found'}, status=status.HTTP_404_NOT_FOUND)
    except Policy.DoesNotExist:
        return Response({'error': 'Policy not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error approving framework policy: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([AllowAny])
def approve_framework_subpolicy(request, framework_id, policy_id, subpolicy_id):
    """
    Approve a subpolicy within a framework policy
    """
    try:
        framework = Framework.objects.get(FrameworkId=framework_id)
        policy = Policy.objects.get(PolicyId=policy_id, FrameworkId=framework)
        subpolicy = SubPolicy.objects.get(SubPolicyId=subpolicy_id, PolicyId=policy)
        
        # Update subpolicy status
        subpolicy.Status = 'Approved'
        subpolicy.save()
        
        # Check if all subpolicies of this policy are now approved
        all_subpolicies = SubPolicy.objects.filter(PolicyId=policy)
        all_subpolicies_approved = all(sub.Status == 'Approved' for sub in all_subpolicies)
        
        response_data = {
            'message': 'Subpolicy approved successfully',
            'SubPolicyId': subpolicy_id,
            'Status': subpolicy.Status,
            'PolicyUpdated': False,
            'FrameworkUpdated': False
        }
        
        if all_subpolicies_approved:
            # Automatically approve the policy
            policy.Status = 'Approved'
            policy.save()
            
            response_data['PolicyUpdated'] = True
            response_data['PolicyStatus'] = 'Approved'
            response_data['message'] = 'Subpolicy approved and policy automatically approved'
            
            # Check if all policies in the framework are now approved
            all_framework_policies = Policy.objects.filter(FrameworkId=framework)
            all_policies_approved = all(pol.Status == 'Approved' for pol in all_framework_policies)
            
            if all_policies_approved:
                # Automatically approve the framework
                framework.Status = 'Approved'
                framework.ActiveInactive = 'Active'
                framework.save()
                
                response_data['FrameworkUpdated'] = True
                response_data['FrameworkStatus'] = 'Approved'
                response_data['message'] = 'Subpolicy approved, policy approved, and framework automatically approved'
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Framework.DoesNotExist:
        return Response({'error': 'Framework not found'}, status=status.HTTP_404_NOT_FOUND)
    except Policy.DoesNotExist:
        return Response({'error': 'Policy not found'}, status=status.HTTP_404_NOT_FOUND)
    except SubPolicy.DoesNotExist:
        return Response({'error': 'Subpolicy not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error approving framework subpolicy: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['PUT'])
@permission_classes([AllowAny])
def reject_framework_subpolicy(request, framework_id, policy_id, subpolicy_id):
    """
    Reject a subpolicy within a framework policy
    """
    try:
        framework = Framework.objects.get(FrameworkId=framework_id)
        policy = Policy.objects.get(PolicyId=policy_id, FrameworkId=framework)
        subpolicy = SubPolicy.objects.get(SubPolicyId=subpolicy_id, PolicyId=policy)
        
        remarks = request.data.get('remarks', '')
        
        # Update subpolicy status
        subpolicy.Status = 'Rejected'
        subpolicy.save()
        
        # Automatically reject the policy since one of its subpolicies is rejected
        policy.Status = 'Rejected'
        policy.save()
        
        # Automatically reject the framework since one of its policies is rejected
        framework.Status = 'Rejected'
        framework.ActiveInactive = 'Inactive'
        framework.save()
        
        response_data = {
            'message': 'Subpolicy rejected, policy and framework automatically rejected',
            'SubPolicyId': subpolicy_id,
            'Status': subpolicy.Status,
            'PolicyUpdated': True,
            'PolicyStatus': 'Rejected',
            'FrameworkUpdated': True,
            'FrameworkStatus': 'Rejected',
            'remarks': remarks
        }
        
        return Response(response_data, status=status.HTTP_200_OK)
        
    except Framework.DoesNotExist:
        return Response({'error': 'Framework not found'}, status=status.HTTP_404_NOT_FOUND)
    except Policy.DoesNotExist:
        return Response({'error': 'Policy not found'}, status=status.HTTP_404_NOT_FOUND)
    except SubPolicy.DoesNotExist:
        return Response({'error': 'Subpolicy not found'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        print(f"Error rejecting framework subpolicy: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_rejected_frameworks_with_hierarchy(request):
    """
    Get all rejected frameworks with their policies and subpolicies for editing
    """
    try:
        print("[DEBUG] Fetching rejected frameworks with hierarchy...")
        
        # Get rejected framework approvals
        rejected_approvals = FrameworkApproval.objects.filter(
            ApprovedNot__in=[0, False]
        ).order_by('-ApprovalId')
        
        print(f"[DEBUG] Found {rejected_approvals.count()} rejected approvals")
        
        # Get unique framework IDs for rejected frameworks
        unique_rejected_frameworks = {}
        
        for approval in rejected_approvals:
            framework_id = approval.FrameworkId.FrameworkId if approval.FrameworkId else None
            if framework_id and framework_id not in unique_rejected_frameworks:
                unique_rejected_frameworks[framework_id] = approval
        
        print(f"[DEBUG] Unique rejected frameworks: {len(unique_rejected_frameworks)}")
        
        rejected_frameworks_data = []
        
        for framework_id, approval in unique_rejected_frameworks.items():
            try:
                framework = approval.FrameworkId
                print(f"[DEBUG] Processing rejected framework {framework_id}: {framework.FrameworkName}")
                
                # Get all policies in this framework directly from database
                policies = Policy.objects.filter(FrameworkId=framework)
                policies_data = []
                
                print(f"[DEBUG] Found {policies.count()} policies for framework {framework_id}")
                
                for policy in policies:
                    print(f"[DEBUG] Processing policy {policy.PolicyId}: {policy.PolicyName} (Status: {policy.Status})")
                    
                    # Get all subpolicies for this policy directly from database
                    subpolicies = SubPolicy.objects.filter(PolicyId=policy)
                    subpolicies_data = []
                    
                    print(f"[DEBUG] Found {subpolicies.count()} subpolicies for policy {policy.PolicyId}")
                    
                    for subpolicy in subpolicies:
                        print(f"[DEBUG] Processing subpolicy {subpolicy.SubPolicyId}: {subpolicy.SubPolicyName} (Status: {subpolicy.Status})")
                        
                        subpolicy_data = {
                            "SubPolicyId": subpolicy.SubPolicyId,
                            "SubPolicyName": subpolicy.SubPolicyName,
                            "Identifier": subpolicy.Identifier,
                            "Description": subpolicy.Description,
                            "Status": subpolicy.Status,
                            "Control": subpolicy.Control,
                            "CreatedByName": subpolicy.CreatedByName,
                            "CreatedByDate": subpolicy.CreatedByDate.isoformat() if subpolicy.CreatedByDate else None,
                            "PermanentTemporary": subpolicy.PermanentTemporary,
                            "approval": {
                                "approved": True if subpolicy.Status == 'Approved' else False if subpolicy.Status == 'Rejected' else None,
                                "remarks": ""
                            },
                            "canEdit": subpolicy.Status == 'Rejected',
                            "version": "u1"
                        }
                        subpolicies_data.append(subpolicy_data)
                    
                    policy_data = {
                        "PolicyId": policy.PolicyId,
                        "PolicyName": policy.PolicyName,
                        "PolicyDescription": policy.PolicyDescription,
                        "Status": policy.Status,
                        "Scope": policy.Scope,
                        "Objective": policy.Objective,
                        "Department": policy.Department,
                        "StartDate": policy.StartDate.isoformat() if policy.StartDate else None,
                        "EndDate": policy.EndDate.isoformat() if policy.EndDate else None,
                        "Identifier": policy.Identifier,
                        "CreatedByName": policy.CreatedByName,
                        "CreatedByDate": policy.CreatedByDate.isoformat() if policy.CreatedByDate else None,
                        "Applicability": policy.Applicability,
                        "PermanentTemporary": policy.PermanentTemporary,
                        "subpolicies": subpolicies_data,
                        "approval": {
                            "approved": True if policy.Status == 'Approved' else False if policy.Status == 'Rejected' else None,
                            "remarks": ""
                        },
                        "canEdit": policy.Status == 'Rejected',
                        "version": "u1",
                        "type": "policy"
                    }
                    policies_data.append(policy_data)
                
                print(f"[DEBUG] Processed {len(policies_data)} policies for framework {framework_id}")
                
                # Create framework data with fresh database info
                framework_data = {
                    "FrameworkId": framework.FrameworkId,
                    "FrameworkName": framework.FrameworkName,
                    "FrameworkDescription": framework.FrameworkDescription,
                    "Category": framework.Category,
                    "EffectiveDate": framework.EffectiveDate.isoformat() if framework.EffectiveDate else None,
                    "StartDate": framework.StartDate.isoformat() if framework.StartDate else None,
                    "EndDate": framework.EndDate.isoformat() if framework.EndDate else None,
                    "CreatedByName": framework.CreatedByName,
                    "CreatedByDate": framework.CreatedByDate.isoformat() if framework.CreatedByDate else None,
                    "Identifier": framework.Identifier,
                    "Status": framework.Status,
                    "ActiveInactive": framework.ActiveInactive,
                    "policies": policies_data,
                    "type": "framework",
                    "approval": {
                        "approved": False,
                        "remarks": approval.ExtractedData.get('framework_approval', {}).get('remarks', '') if approval.ExtractedData else ''
                    }
                }
                
                rejected_framework = {
                    "ApprovalId": approval.ApprovalId,
                    "FrameworkId": framework.FrameworkId,
                    "ExtractedData": framework_data,
                    "UserId": approval.UserId,
                    "ReviewerId": approval.ReviewerId,
                    "Version": approval.Version,
                    "ApprovedNot": approval.ApprovedNot,
                    "rejection_reason": approval.ExtractedData.get('framework_approval', {}).get('remarks', 'No reason provided') if approval.ExtractedData else 'No reason provided'
                }
                
                rejected_frameworks_data.append(rejected_framework)
                print(f"[DEBUG] Added rejected framework {framework_id} to response")
                
            except Exception as e:
                print(f"Error processing rejected framework {framework_id}: {str(e)}")
                import traceback
                traceback.print_exc()
                continue
        
        print(f"[DEBUG] Returning {len(rejected_frameworks_data)} rejected frameworks with hierarchy")
        return Response(rejected_frameworks_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error getting rejected frameworks with hierarchy: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_pending_framework_approvals_for_reviewer(request):
    """
    Get all pending framework approvals for reviewer (including resubmitted frameworks)
    """
    try:
        print("[DEBUG] Fetching pending framework approvals for reviewer...")
        
        # Get all framework approvals that are pending (ApprovedNot is None/null)
        pending_approvals = FrameworkApproval.objects.filter(
            ApprovedNot__isnull=True
        ).order_by('-ApprovalId')
        
        print(f"[DEBUG] Found {pending_approvals.count()} pending framework approvals")
        
        # Get unique framework IDs with their latest versions
        unique_pending_frameworks = {}
        
        for approval in pending_approvals:
            framework_id = approval.FrameworkId.FrameworkId if approval.FrameworkId else None
            if framework_id:
                # Only keep the latest version for each framework
                if framework_id not in unique_pending_frameworks:
                    unique_pending_frameworks[framework_id] = approval
                    print(f"[DEBUG] Added framework {framework_id} with version {approval.Version}")
                else:
                    # Compare versions and keep the latest
                    current_version = unique_pending_frameworks[framework_id].Version or 'u1'
                    new_version = approval.Version or 'u1'
                    
                    # If this is a newer version, replace it
                    if approval.ApprovalId > unique_pending_frameworks[framework_id].ApprovalId:
                        unique_pending_frameworks[framework_id] = approval
                        print(f"[DEBUG] Updated framework {framework_id} to newer version {approval.Version}")
        
        pending_approvals_data = []
        
        for framework_id, approval in unique_pending_frameworks.items():
            try:
                framework = approval.FrameworkId
                print(f"[DEBUG] Processing pending framework {framework_id}: {framework.FrameworkName} (Version: {approval.Version})")
                
                # Get fresh data from database for policies and subpolicies
                policies = Policy.objects.filter(FrameworkId=framework)
                policies_data = []
                
                for policy in policies:
                    # Get subpolicies for this policy
                    subpolicies = SubPolicy.objects.filter(PolicyId=policy)
                    subpolicies_data = []
                    
                    for subpolicy in subpolicies:
                        subpolicy_data = {
                            "SubPolicyId": subpolicy.SubPolicyId,
                            "SubPolicyName": subpolicy.SubPolicyName,
                            "Identifier": subpolicy.Identifier,
                            "Description": subpolicy.Description,
                            "Status": subpolicy.Status,
                            "Control": subpolicy.Control,
                            "CreatedByName": subpolicy.CreatedByName,
                            "CreatedByDate": subpolicy.CreatedByDate.isoformat() if subpolicy.CreatedByDate else None,
                            "PermanentTemporary": subpolicy.PermanentTemporary,
                            "approval": {
                                "approved": True if subpolicy.Status == 'Approved' else False if subpolicy.Status == 'Rejected' else None,
                                "remarks": ""
                            },
                            "version": "u1"
                        }
                        subpolicies_data.append(subpolicy_data)
                    
                    policy_data = {
                        "PolicyId": policy.PolicyId,
                        "PolicyName": policy.PolicyName,
                        "PolicyDescription": policy.PolicyDescription,
                        "Status": policy.Status,
                        "Scope": policy.Scope,
                        "Objective": policy.Objective,
                        "Department": policy.Department,
                        "StartDate": policy.StartDate.isoformat() if policy.StartDate else None,
                        "EndDate": policy.EndDate.isoformat() if policy.EndDate else None,
                        "Identifier": policy.Identifier,
                        "CreatedByName": policy.CreatedByName,
                        "CreatedByDate": policy.CreatedByDate.isoformat() if policy.CreatedByDate else None,
                        "Applicability": policy.Applicability,
                        "PermanentTemporary": policy.PermanentTemporary,
                        "subpolicies": subpolicies_data,
                        "approval": {
                            "approved": True if policy.Status == 'Approved' else False if policy.Status == 'Rejected' else None,
                            "remarks": ""
                        },
                        "version": "u1",
                        "type": "policy"
                    }
                    policies_data.append(policy_data)
                
                # Create the approval data with fresh framework info
                approval_data = {
                    "ApprovalId": approval.ApprovalId,
                    "FrameworkId": framework.FrameworkId,
                    "ExtractedData": approval.ExtractedData if approval.ExtractedData else {
                        "FrameworkId": framework.FrameworkId,
                        "FrameworkName": framework.FrameworkName,
                        "FrameworkDescription": framework.FrameworkDescription,
                        "Category": framework.Category,
                        "EffectiveDate": framework.EffectiveDate.isoformat() if framework.EffectiveDate else None,
                        "StartDate": framework.StartDate.isoformat() if framework.StartDate else None,
                        "EndDate": framework.EndDate.isoformat() if framework.EndDate else None,
                        "CreatedByName": framework.CreatedByName,
                        "CreatedByDate": framework.CreatedByDate.isoformat() if framework.CreatedByDate else None,
                        "Identifier": framework.Identifier,
                        "Status": framework.Status,
                        "ActiveInactive": framework.ActiveInactive,
                        "policies": policies_data,
                        "type": "framework"
                    },
                    "UserId": approval.UserId,
                    "ReviewerId": approval.ReviewerId,
                    "Version": approval.Version,
                    "ApprovedNot": approval.ApprovedNot,
                    "ApprovedDate": approval.ApprovedDate.isoformat() if approval.ApprovedDate else None,
                    "isResubmitted": approval.Version and (approval.Version.startswith('u') and approval.Version != 'u1')
                }
                
                # Ensure ExtractedData has the policies
                if approval_data["ExtractedData"] and "policies" not in approval_data["ExtractedData"]:
                    approval_data["ExtractedData"]["policies"] = policies_data
                
                pending_approvals_data.append(approval_data)
                print(f"[DEBUG] Added pending framework approval {approval.ApprovalId} with {len(policies_data)} policies")
                
            except Exception as e:
                print(f"Error processing pending framework {framework_id}: {str(e)}")
                continue
        
        print(f"[DEBUG] Returning {len(pending_approvals_data)} pending framework approvals for reviewer")
        return Response(pending_approvals_data, status=status.HTTP_200_OK)
        
    except Exception as e:
        print(f"Error getting pending framework approvals for reviewer: {str(e)}")
        import traceback
        traceback.print_exc()
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 