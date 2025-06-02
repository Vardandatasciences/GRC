from django.db import connection
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.utils import timezone
import json
from .models import Audit, AuditReport

@api_view(['GET'])
def check_audit_reports(request):
    """
    Check for existing audit reports based on framework, policy, and subpolicy IDs
    """
    try:
        framework_id = request.GET.get('framework_id')
        policy_id = request.GET.get('policy_id')
        subpolicy_id = request.GET.get('subpolicy_id')

        if not framework_id:
            return Response({'error': 'Framework ID is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Build query based on provided parameters
        query = """
            SELECT 
                ar.ReportId,
                a.CompletionDate,
                auditor.UserName as AuditorName,
                reviewer.UserName as ReviewerName
            FROM 
                audit_report ar
                JOIN audit a ON ar.AuditId = a.AuditId
                JOIN users auditor ON a.auditor = auditor.UserId
                LEFT JOIN users reviewer ON a.reviewer = reviewer.UserId
            WHERE 
                ar.FrameworkId = %s
        """
        params = [framework_id]

        if policy_id:
            query += " AND ar.PolicyId = %s"
            params.append(policy_id)
        else:
            query += " AND ar.PolicyId IS NULL"

        if subpolicy_id:
            query += " AND ar.SubPolicyId = %s"
            params.append(subpolicy_id)
        else:
            query += " AND ar.SubPolicyId IS NULL"

        with connection.cursor() as cursor:
            cursor.execute(query, params)
            columns = [col[0] for col in cursor.description]
            reports = [dict(zip(columns, row)) for row in cursor.fetchall()]

            # Format dates
            for report in reports:
                if report.get('CompletionDate'):
                    report['CompletionDate'] = report['CompletionDate'].strftime('%Y-%m-%d %H:%M:%S')

        return Response({'reports': reports}, status=status.HTTP_200_OK)

    except Exception as e:
        print(f"ERROR in check_audit_reports: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

def handle_selected_reports(audit, selected_reports):
    """
    Handle selected reports for an audit
    """
    try:
        if not selected_reports:
            return

        reports_json = []
        for report_id in selected_reports:
            try:
                report = AuditReport.objects.get(ReportId=report_id)
                reports_json.append({
                    'report_id': report.ReportId,
                    'audit_id': report.AuditId.AuditId,
                    'report': report.Report
                })
            except AuditReport.DoesNotExist:
                continue
        
        if reports_json:
            audit.Report = json.dumps(reports_json)
            audit.save()
            print(f"Successfully saved {len(reports_json)} reports to audit {audit.AuditId}")
            
    except Exception as e:
        print(f"ERROR in handle_selected_reports: {str(e)}")
        # Don't raise the exception, just log it
        pass 

@api_view(['GET'])
def get_report_details(request):
    """
    Get details for specific report IDs
    """
    try:
        report_ids_str = request.GET.get('report_ids', '')
        
        if not report_ids_str:
            return Response({'error': 'No report IDs provided'}, status=status.HTTP_400_BAD_REQUEST)
            
        # Split and clean the report IDs
        report_ids = [int(id.strip()) for id in report_ids_str.split(',') if id.strip()]
        
        if not report_ids:
            return Response({'error': 'No valid report IDs found'}, status=status.HTTP_400_BAD_REQUEST)

        # Build query to get report details with proper joins
        query = """
            SELECT 
                ar.ReportId as report_id,
                ar.Report as report,
                a.CompletionDate as report_date,
                auditor.UserName as auditor,
                reviewer.UserName as reviewer
            FROM audit_report ar
            JOIN audit a ON ar.AuditId = a.AuditId
            JOIN users auditor ON a.Auditor = auditor.UserId
            LEFT JOIN users reviewer ON a.Reviewer = reviewer.UserId
            WHERE ar.ReportId IN %s
        """
        
        with connection.cursor() as cursor:
            cursor.execute(query, [tuple(report_ids)])
            columns = [col[0] for col in cursor.description]
            reports = [dict(zip(columns, row)) for row in cursor.fetchall()]
            
            # Format dates
            for report in reports:
                if report.get('report_date'):
                    report['report_date'] = report['report_date'].strftime('%Y-%m-%d')
            
            if not reports:
                return Response({'error': 'No reports found'}, status=status.HTTP_404_NOT_FOUND)
                
            return Response({'reports': reports})
            
    except Exception as e:
        print(f"Error in get_report_details: {str(e)}")
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR) 