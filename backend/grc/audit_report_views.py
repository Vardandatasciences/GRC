from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import Audit

@api_view(['GET'])
def get_audit_reports(request):
    """
    Get all completed audits for report viewing
    """
    try:
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    a.AuditId,
                    f.FrameworkName as Framework,
                    p.PolicyName as Policy,
                    sp.SubPolicyName as SubPolicy,
                    u_assignee.UserName as Assigned,
                    u_auditor.UserName as Auditor,
                    u_reviewer.UserName as Reviewer,
                    a.CompletionDate
                FROM 
                    audit a
                JOIN
                    frameworks f ON a.FrameworkId = f.FrameworkId
                LEFT JOIN
                    policies p ON a.PolicyId = p.PolicyId
                LEFT JOIN
                    subpolicies sp ON a.SubPolicyId = sp.SubPolicyId
                JOIN
                    users u_assignee ON a.assignee = u_assignee.UserId
                JOIN
                    users u_auditor ON a.auditor = u_auditor.UserId
                LEFT JOIN
                    users u_reviewer ON a.reviewer = u_reviewer.UserId
                WHERE
                    a.Status = 'Completed'
                ORDER BY
                    a.CompletionDate DESC
            """)
            
            columns = [col[0] for col in cursor.description]
            audits = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Format dates
        for audit in audits:
            if audit.get('CompletionDate'):
                audit['CompletionDate'] = audit['CompletionDate'].strftime('%d/%m/%Y')
        
        return Response({
            'audits': audits
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"ERROR in get_audit_reports: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_audit_report_versions(request, audit_id):
    """
    Get all report versions (R versions) for a specific audit
    """
    try:
        # Check if the audit exists
        try:
            audit = Audit.objects.get(AuditId=audit_id)
        except Audit.DoesNotExist:
            return Response({'error': 'Audit not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Get all R versions for this audit
        with connection.cursor() as cursor:
            print(f"DEBUG: Fetching R versions for audit_id: {audit_id}")
            
            # First, let's check what values are in the database
            cursor.execute("""
                SELECT 
                    Version, 
                    ApprovedRejected,
                    ActiveInactive
                FROM 
                    audit_version 
                WHERE 
                    AuditId = %s 
                    AND Version LIKE 'R%%'
            """, [audit_id])
            
            debug_rows = cursor.fetchall()
            for row in debug_rows:
                print(f"DEBUG: Version: {row[0]}, ApprovedRejected: {row[1]}, ActiveInactive: {row[2] if len(row) > 2 else 'N/A'}")
            
            # Now execute the actual query with special handling for R1 and R2
            # Only show active versions (ActiveInactive = 'A')
            cursor.execute("""
                SELECT 
                    av.Version,
                    av.Date,
                    CASE 
                        WHEN av.ApprovedRejected = 1 OR av.ApprovedRejected = '1' THEN 'Approved'
                        WHEN av.ApprovedRejected = 2 OR av.ApprovedRejected = '2' THEN 'Rejected'
                        ELSE 'Pending'
                    END as ReportStatus,
                    av.ApprovedRejected,
                    av.ActiveInactive
                FROM 
                    audit_version av
                WHERE 
                    av.AuditId = %s
                    AND av.Version LIKE 'R%%'
                    AND (av.ActiveInactive = 'A' OR av.ActiveInactive IS NULL)
                ORDER BY 
                    av.Version DESC
            """, [audit_id])
            
            columns = [col[0] for col in cursor.description]
            versions = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        # Log versions for debugging
        for version in versions:
            print(f"DEBUG: Result - Version: {version.get('Version')}, ActiveInactive: {version.get('ActiveInactive')}")
        
        # Format date for each version with time included
        for version in versions:
            if version.get('Date'):
                version['Date'] = version['Date'].strftime('%d/%m/%Y %H:%M')
        
        return Response({
            'audit_id': audit_id,
            'versions': versions
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"ERROR in get_audit_report_versions: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
def delete_audit_report_version(request, audit_id, version):
    """
    Mark a report version as inactive (soft delete)
    """
    try:
        # Check if the audit exists
        try:
            audit = Audit.objects.get(AuditId=audit_id)
        except Audit.DoesNotExist:
            return Response({'error': 'Audit not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Update the version to set ActiveInactive to 'I'
        with connection.cursor() as cursor:
            print(f"DEBUG: Marking version {version} as inactive for audit_id: {audit_id}")
            
            cursor.execute("""
                UPDATE audit_version 
                SET ActiveInactive = 'I'
                WHERE AuditId = %s AND Version = %s
            """, [audit_id, version])
            
            # Check if the update was successful
            if cursor.rowcount == 0:
                return Response({'error': 'Version not found'}, status=status.HTTP_404_NOT_FOUND)
        
        return Response({
            'success': True,
            'message': f'Successfully marked version {version} as inactive'
        }, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"ERROR in delete_audit_report_version: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def get_audit_report_s3_link(request, audit_id, version):
    """
    Get the S3 link for a specific audit report version
    """
    try:
        # Check if the audit exists
        try:
            audit = Audit.objects.get(AuditId=audit_id)
        except Audit.DoesNotExist:
            return Response({'error': 'Audit not found'}, status=status.HTTP_404_NOT_FOUND)
        
        # Check if the requested version exists and if it's an approved version
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    ApprovedRejected 
                FROM 
                    audit_version 
                WHERE 
                    AuditId = %s 
                    AND Version = %s
                    AND (ActiveInactive = 'A' OR ActiveInactive IS NULL)
            """, [audit_id, version])
            
            version_status_row = cursor.fetchone()
            if not version_status_row:
                return Response({'error': 'Version not found'}, status=status.HTTP_404_NOT_FOUND)
            
            version_status = version_status_row[0]
            is_rejected = False
            
            # Check if the version is rejected
            if version == 'R1' or version_status == '2' or version_status == 2:
                is_rejected = True
                return Response({
                    'error': 'Cannot download rejected reports',
                    'is_rejected': True
                }, status=status.HTTP_403_FORBIDDEN)
            
            # Get the S3 link from audit_report table
            cursor.execute("""
                SELECT 
                    Report 
                FROM 
                    audit_report 
                WHERE 
                    AuditId = %s
            """, [audit_id])
            
            report_row = cursor.fetchone()
            if not report_row or not report_row[0]:
                return Response({'error': 'Report not found in S3'}, status=status.HTTP_404_NOT_FOUND)
            
            s3_link = report_row[0]
            
            return Response({
                'audit_id': audit_id,
                'version': version,
                's3_link': s3_link
            }, status=status.HTTP_200_OK)
    
    except Exception as e:
        print(f"ERROR in get_audit_report_s3_link: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)