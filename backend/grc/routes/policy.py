from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from ..models import Policy, SubPolicy, PolicyApproval, PolicyVersion
from ..serializers import PolicySerializer, SubPolicySerializer, PolicyApprovalSerializer
import traceback
from django.db import transaction
import datetime

@api_view(['GET'])
@permission_classes([AllowAny])
def get_policies_by_framework(request, framework_id):
    """
    Get all policies for a specific framework
    """
    try:
        policies = Policy.objects.filter(FrameworkId=framework_id)
        serializer = PolicySerializer(policies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        error_info = {
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        return Response({'error': 'Error retrieving policies', 'details': error_info}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_subpolicies_by_policy(request, policy_id):
    """
    Get all subpolicies for a specific policy
    """
    try:
        subpolicies = SubPolicy.objects.filter(PolicyId=policy_id)
        serializer = SubPolicySerializer(subpolicies, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        error_info = {
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        return Response({'error': 'Error retrieving subpolicies', 'details': error_info}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def policy_detail(request, pk):
    """
    Retrieve, update or delete a policy.
    """
    try:
        policy = Policy.objects.get(PolicyId=pk)
    except Policy.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = PolicySerializer(policy)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        # Make a copy of the request data
        data = request.data.copy()
        
        # Remove the restriction that only approved and active policies can be updated
        # Allow any policy to be updated, regardless of status
        serializer = PolicySerializer(policy, data=data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        policy.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET', 'POST'])
@permission_classes([AllowAny])
def policy_list(request):
    """
    List all policies or create a new policy
    """
    if request.method == 'GET':
        # Get filter parameters
        status_filter = request.GET.get('status', None)
        
        # Start with all policies
        policies = Policy.objects.all()
        
        # Apply status filter if provided
        if status_filter:
            policies = policies.filter(Status=status_filter)
            
        serializer = PolicySerializer(policies, many=True)
        return Response(serializer.data)
    
    elif request.method == 'POST':
        serializer = PolicySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def add_policy_to_framework(request, framework_id):
    """
    Add a new policy to an existing framework
    """
    try:
        with transaction.atomic():
            # Copy request data and add framework_id
            data = request.data.copy()
            data['FrameworkId'] = framework_id
            
            # Set default values
            data.setdefault('Status', 'Under Review')
            data.setdefault('ActiveInactive', 'Inactive')
            data.setdefault('CurrentVersion', 1.0)
            data.setdefault('CreatedByDate', datetime.date.today())
            
            # Create the policy
            policy_serializer = PolicySerializer(data=data)
            if not policy_serializer.is_valid():
                return Response(policy_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            policy = policy_serializer.save()
            
            # Create policy version
            policy_version = PolicyVersion(
                PolicyId=policy,
                Version=policy.CurrentVersion,
                PolicyName=policy.PolicyName,
                CreatedBy=policy.CreatedByName,
                CreatedDate=datetime.date.today(),
                PreviousVersionId=None
            )
            policy_version.save()
            
            # Handle subpolicies if provided
            subpolicies_data = request.data.get('subpolicies', [])
            for subpolicy_data in subpolicies_data:
                subpolicy_data = subpolicy_data.copy()
                subpolicy_data['PolicyId'] = policy.PolicyId
                subpolicy_data.setdefault('Status', 'Under Review')
                subpolicy_data.setdefault('CreatedByName', policy.CreatedByName)
                subpolicy_data['CreatedByDate'] = datetime.date.today()
                
                subpolicy_serializer = SubPolicySerializer(data=subpolicy_data)
                if not subpolicy_serializer.is_valid():
                    return Response(subpolicy_serializer.errors, status=status.HTTP_400_BAD_REQUEST)
                
                subpolicy_serializer.save()
            
            return Response({
                'message': 'Policy added to framework successfully',
                'PolicyId': policy.PolicyId,
                'CurrentVersion': policy.CurrentVersion
            }, status=status.HTTP_201_CREATED)
    except Exception as e:
        error_info = {
            'error': str(e),
            'traceback': traceback.format_exc()
        }
        return Response({'error': 'Error adding policy to framework', 'details': error_info}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET', 'PUT', 'DELETE'])
@permission_classes([AllowAny])
def subpolicy_detail(request, pk):
    """
    Retrieve, update or delete a subpolicy.
    """
    try:
        subpolicy = SubPolicy.objects.get(SubPolicyId=pk)
    except SubPolicy.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
    
    if request.method == 'GET':
        serializer = SubPolicySerializer(subpolicy)
        return Response(serializer.data)
    
    elif request.method == 'PUT':
        serializer = SubPolicySerializer(subpolicy, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    elif request.method == 'DELETE':
        subpolicy.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['PUT'])
@permission_classes([AllowAny])
def submit_subpolicy_review(request, pk):
    """
    Submit a review for a subpolicy
    """
    try:
        subpolicy = SubPolicy.objects.get(SubPolicyId=pk)
    except SubPolicy.DoesNotExist:
        return Response({'error': 'Subpolicy not found'}, status=status.HTTP_404_NOT_FOUND)
    
    # Update status based on review submission
    status_value = request.data.get('Status')
    remarks = request.data.get('remarks', '')
    
    if status_value:
        subpolicy.Status = status_value
        subpolicy.save()
    
    # Check if this update impacts the parent policy
    if status_value == 'Approved':
        # Check if all subpolicies of this policy are approved
        policy = subpolicy.PolicyId
        all_subpolicies = SubPolicy.objects.filter(PolicyId=policy)
        all_approved = all(sub.Status == 'Approved' for sub in all_subpolicies)
        
        if all_approved:
            # Automatically approve the parent policy
            policy.Status = 'Approved'
            policy.save()
            
            response_data = {
                'message': 'Subpolicy review submitted successfully and policy updated',
                'SubPolicyId': pk,
                'Status': status_value,
                'PolicyUpdated': True,
                'PolicyStatus': 'Approved'
            }
        else:
            response_data = {
                'message': 'Subpolicy review submitted successfully',
                'SubPolicyId': pk,
                'Status': status_value,
                'PolicyUpdated': False
            }
    else:
        response_data = {
            'message': 'Subpolicy review submitted successfully',
            'SubPolicyId': pk,
            'Status': status_value,
            'PolicyUpdated': False
        }
    
    return Response(response_data, status=status.HTTP_200_OK)

@api_view(['PUT'])
@permission_classes([AllowAny])
def resubmit_subpolicy(request, pk):
    """
    Resubmit a rejected subpolicy with changes
    """
    try:
        subpolicy = SubPolicy.objects.get(SubPolicyId=pk)
        policy_id = subpolicy.PolicyId.PolicyId

        # Get all versions for this policy to find the latest u version
        policy_approvals = PolicyApproval.objects.filter(
            PolicyId=policy_id
        ).order_by('-Version')

        # Find the latest u version - use Python filtering instead of query filtering
        u_versions = [pa.Version for pa in policy_approvals if pa.Version and pa.Version.startswith('u')]
        new_version = 'u1'

        if u_versions:
            # Get the highest u version number
            latest_u_num = max([int(v[1:]) for v in u_versions if v[1:].isdigit()])
            new_version = f'u{latest_u_num + 1}'

        # Update subpolicy with new data
        data = request.data.copy()
        
        if 'Description' in data:
            subpolicy.Description = data['Description']
        
        if 'Control' in data:
            subpolicy.Control = data['Control']
        
        # Set status back to Under Review
        subpolicy.Status = 'Under Review'
        
        # Save the changes
        subpolicy.save()

        # Create new policy approval with incremented u version
        policy = Policy.objects.get(PolicyId=policy_id)
        
        # Get the latest policy approval to copy its data
        latest_approval = policy_approvals.first()
        if latest_approval:
            extracted_data = latest_approval.ExtractedData.copy()
            
            # Update the specific subpolicy in extracted data
            if 'subpolicies' in extracted_data:
                for sub in extracted_data['subpolicies']:
                    if sub.get('SubPolicyId') == pk:
                        sub['Description'] = subpolicy.Description
                        sub['Control'] = subpolicy.Control
                        sub['Status'] = 'Under Review'
                        break

            # Create new policy approval
            new_approval = PolicyApproval(
                PolicyId=policy,
                ExtractedData=extracted_data,
                UserId=latest_approval.UserId,
                ReviewerId=latest_approval.ReviewerId,
                ApprovedNot=None,
                Version=new_version
            )
            new_approval.save()

        # Update policy status if needed
        if policy.Status == 'Rejected':
            policy.Status = 'Under Review'
            policy.save()

        return Response({
            'message': 'Subpolicy resubmitted successfully',
            'SubPolicyId': pk,
            'Status': 'Under Review',
            'version': new_version
        }, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"Error resubmitting subpolicy: {str(e)}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_policy_version(request, policy_id):
    """
    Get the latest version of a policy from the policy approvals table
    """
    try:
        policy = get_object_or_404(Policy, PolicyId=policy_id)
        
        # Instead of getting the attribute, find the latest approval version from the database
        latest_approval = PolicyApproval.objects.filter(
            PolicyId=policy_id
        ).order_by('-Version').first()
        
        # Extract the latest version from policy approvals
        if latest_approval and latest_approval.Version:
            # If version starts with 'u', return it
            if latest_approval.Version.startswith('u'):
                version = latest_approval.Version
            else:
                # Check if there are any user versions (u1, u2, etc.)
                user_approvals = PolicyApproval.objects.filter(
                    PolicyId=policy_id,
                    Version__startswith='u'
                ).order_by('-Version')
                
                if user_approvals.exists():
                    version = user_approvals.first().Version
                else:
                    version = 'u1'  # Default if no user versions found
        else:
            # If no approvals found, default to u1
            version = 'u1'
        
        print(f"Latest version for policy {policy_id}: {version}")
        
        return Response({
            'policy_id': policy_id,
            'version': version
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error getting policy version: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_subpolicy_version(request, subpolicy_id):
    """
    Get the latest version of a subpolicy from policy approvals
    """
    try:
        subpolicy = get_object_or_404(SubPolicy, SubPolicyId=subpolicy_id)
        policy_id = subpolicy.PolicyId.PolicyId if subpolicy.PolicyId else None
        
        if not policy_id:
            return Response({
                'subpolicy_id': subpolicy_id,
                'version': 'u1',
                'error': 'No parent policy found'
            }, status=status.HTTP_200_OK)
        
        # Find the latest policy approval with this subpolicy
        latest_version = 'u1'  # Default version
        
        try:
            # Get all policy approvals for the parent policy
            policy_approvals = PolicyApproval.objects.filter(
                PolicyId=policy_id
            ).order_by('-Version')
            
            # Look through policy approvals for this subpolicy
            for approval in policy_approvals:
                if not approval.ExtractedData or 'subpolicies' not in approval.ExtractedData:
                    continue
                
                # Find this subpolicy in the extracted data
                for sub in approval.ExtractedData['subpolicies']:
                    if sub.get('SubPolicyId') == subpolicy_id:
                        # Found a reference to this subpolicy
                        if approval.Version and approval.Version.startswith('u'):
                            latest_version = approval.Version
                            # We found a user version, return it
                            print(f"Found version {latest_version} for subpolicy {subpolicy_id}")
                            return Response({
                                'subpolicy_id': subpolicy_id,
                                'version': latest_version
                            }, status=status.HTTP_200_OK)
            
            # If we got here and didn't find a user version, check the subpolicy object
            stored_version = getattr(subpolicy, 'version', None)
            if stored_version and stored_version.startswith('u'):
                latest_version = stored_version
        except Exception as inner_error:
            print(f"Error finding version in approvals: {str(inner_error)}")
            # Continue with default version
        
        print(f"Latest version for subpolicy {subpolicy_id}: {latest_version}")
        
        return Response({
            'subpolicy_id': subpolicy_id,
            'version': latest_version
        }, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error getting subpolicy version: {str(e)}")
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_latest_policy_approval(request, policy_id):
    """
    Get the latest policy approval for a policy
    """
    try:
        latest_approval = PolicyApproval.objects.filter(
            PolicyId=policy_id
        ).order_by('-Version').first()
        
        if not latest_approval:
            return Response({'error': 'No approval found for this policy'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PolicyApprovalSerializer(latest_approval)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_latest_policy_approval_by_role(request, policy_id, role):
    """
    Get the latest policy approval for a policy by role (reviewer/user)
    """
    try:
        # Filter by role - simplistic approach, you might need more complex logic
        if role == 'reviewer':
            latest_approval = PolicyApproval.objects.filter(
                PolicyId=policy_id,
                IsReviewer=True
            ).order_by('-Version').first()
        else:  # user role
            latest_approval = PolicyApproval.objects.filter(
                PolicyId=policy_id,
                IsReviewer=False
            ).order_by('-Version').first()
        
        if not latest_approval:
            return Response({'error': f'No {role} approval found for this policy'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = PolicyApprovalSerializer(latest_approval)
        return Response(serializer.data)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_latest_reviewer_version(request, policy_id=None, subpolicy_id=None):
    """
    Get the latest reviewer version (R1, R2, etc.) for a policy or subpolicy
    and return the complete policy approval data for that version
    """
    try:
        latest_r_version = 'R1'  # Default if no reviewer versions found
        policy_approval_data = None
        
        if policy_id:
            # Find the latest R version for a policy
            policy = get_object_or_404(Policy, PolicyId=policy_id)
            
            # Use Python filtering instead of MySQL regex to avoid character set issues
            r_approvals = []
            all_approvals = PolicyApproval.objects.filter(PolicyId=policy_id).order_by('-Version')
            
            for approval in all_approvals:
                if approval.Version and approval.Version.startswith('R'):
                    r_approvals.append(approval)
            
            if r_approvals:
                # Get the latest policy approval with R version
                latest_approval = r_approvals[0]
                latest_r_version = latest_approval.Version
                print(f"Found latest R version for policy {policy_id}: {latest_r_version}")
                
                # Serialize the policy approval data
                serializer = PolicyApprovalSerializer(latest_approval)
                policy_approval_data = serializer.data
        
        elif subpolicy_id:
            # Find the latest R version for a subpolicy
            subpolicy = get_object_or_404(SubPolicy, SubPolicyId=subpolicy_id)
            policy_id = subpolicy.PolicyId.PolicyId if subpolicy.PolicyId else None
            
            if policy_id:
                # Use Python filtering instead of MySQL regex
                r_approvals = []
                all_approvals = PolicyApproval.objects.filter(PolicyId=policy_id).order_by('-Version')
                
                for approval in all_approvals:
                    if approval.Version and approval.Version.startswith('R'):
                        r_approvals.append(approval)
                
                if r_approvals:
                    # Get the latest policy approval
                    latest_approval = r_approvals[0]
                    latest_r_version = latest_approval.Version
                    
                    # Serialize the policy approval data
                    serializer = PolicyApprovalSerializer(latest_approval)
                    policy_approval_data = serializer.data
                    
                    print(f"Found latest R version for subpolicy {subpolicy_id}: {latest_r_version} in policy {policy_id}")
        
        # If we have policy approval data, return it along with the version
        if policy_approval_data:
            return Response({
                'policy_id': policy_id,
                'subpolicy_id': subpolicy_id,
                'version': latest_r_version,
                'approval_data': policy_approval_data
            }, status=status.HTTP_200_OK)
        else:
            # If no approval data found, just return the version
            return Response({
                'policy_id': policy_id,
                'subpolicy_id': subpolicy_id,
                'version': latest_r_version,
                'approval_data': None
            }, status=status.HTTP_200_OK)
    except Exception as e:
        print(f"Error getting latest reviewer version: {str(e)}")
        traceback.print_exc()
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([AllowAny])
def submit_policy_approval_review(request, policy_id):
    try:
        policy = get_object_or_404(Policy, PolicyId=policy_id)
        
        # Get data from request
        extracted_data = request.data.get('ExtractedData')
        approved_not = request.data.get('ApprovedNot')
        reviewer_id = request.data.get('ReviewerId')
        user_id = request.data.get('UserId')
        
        if not extracted_data:
            return Response({'error': 'ExtractedData is required'}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get all versions for this policy
        policy_approvals = PolicyApproval.objects.filter(
            PolicyId=policy_id
        ).order_by('-Version')
        
        # Initialize version
        new_version = 'R1'  # Default first reviewer version
        
        if policy_approvals:
            # Use list comprehension instead of filter with startswith to avoid BINARY
            r_versions = [pa.Version for pa in policy_approvals if pa.Version and pa.Version.startswith('R')]
            u_versions = [pa.Version for pa in policy_approvals if pa.Version and pa.Version.startswith('u')]
            
            if approved_not is False:  # If rejecting
                # For rejection, we'll create a new u version
                if u_versions:
                    # Get the highest u version number
                    latest_u_num = max([int(v[1:]) for v in u_versions if v[1:].isdigit()])
                    new_version = f'u{latest_u_num + 1}'
                else:
                    new_version = 'u1'
            else:  # For reviewer submission
                if r_versions:
                    # Get the highest R version number
                    latest_r_num = max([int(v[1:]) for v in r_versions if v[1:].isdigit()])
                    new_version = f'R{latest_r_num + 1}'
                else:
                    new_version = 'R1'
        
        # Verify this version doesn't already exist - do a list check instead of query
        existing_versions = [pa.Version for pa in policy_approvals]
        while new_version in existing_versions:
            # If version exists, increment the number
            prefix = new_version[0]
            num = int(new_version[1:]) + 1
            new_version = f'{prefix}{num}'
        
        # Set approved date if policy is approved
        approved_date = datetime.date.today() if approved_not is True or approved_not == 1 else None
        
        # Create new policy approval with incremented version
        new_approval = PolicyApproval(
            PolicyId=policy,
            ExtractedData=extracted_data,
            UserId=user_id,
            ReviewerId=reviewer_id,
            ApprovedNot=approved_not,
            ApprovedDate=approved_date,
            Version=new_version
        )
        new_approval.save()
        
        # Update policy status
        if approved_not is True or approved_not == 1:
            policy.Status = 'Approved'
            policy.ActiveInactive = 'Active'
        elif approved_not is False or approved_not == 0:
            policy.Status = 'Rejected'
        else:
            policy.Status = 'Under Review'
        
        policy.save()
        
        # Update subpolicies if policy is approved
        if approved_not is True or approved_not == 1:
            SubPolicy.objects.filter(PolicyId=policy.PolicyId, Status='Under Review').update(Status='Approved')
        
        return Response({
            'message': 'Policy review submitted successfully',
            'PolicyId': policy.PolicyId,
            'ApprovalId': new_approval.ApprovalId,
            'Version': new_version,
            'Status': policy.Status,
            'ApprovedDate': approved_date.isoformat() if approved_date else None
        }, status=status.HTTP_201_CREATED)
    
    except Exception as e:
        print(f"Error submitting policy review: {str(e)}")
        traceback.print_exc()
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_policy_version_history(request, policy_id):
    """
    Get the version history of a policy
    """
    try:
        approvals = PolicyApproval.objects.filter(
            PolicyId=policy_id
        ).order_by('-Version')
        
        version_history = []
        for approval in approvals:
            version_history.append({
                'version': approval.Version,
                'previousVersion': approval.PreviousVersion,
                'approvedDate': approval.ApprovedDate,
                'status': 'Approved' if approval.ApprovedNot else 'Rejected' if approval.ApprovedNot is False else 'Under Review'
            })
        
        return Response({
            'policy_id': policy_id,
            'versions': version_history
        }, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({
            'error': str(e)
        }, status=status.HTTP_400_BAD_REQUEST)
