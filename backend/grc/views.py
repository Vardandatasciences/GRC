from django.shortcuts import render
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from .serializers import UserSerializer
from rest_framework import viewsets
from .models import Risk
from .serializers import RiskSerializer
from .models import Incident
from .serializers import IncidentSerializer
from .models import Compliance
from .serializers import ComplianceSerializer
from .models import RiskInstance
from .serializers import RiskInstanceSerializer
from .slm_service import analyze_security_incident
from django.http import JsonResponse
from django.db.models import Count, Q, Avg, F, ExpressionWrapper, DurationField, FloatField
from django.db.models.functions import Cast
import random
from datetime import datetime, timedelta
import json
import math
from dateutil.relativedelta import relativedelta
from django.utils import timezone
from django.db import connection
from django.db import models

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
def last_incident(request):
    last = Incident.objects.order_by('-IncidentId').first()
    if last:
        serializer = IncidentSerializer(last)
        return Response(serializer.data)
    else:
        return Response({}, status=404)

@api_view(['GET'])
def get_compliance_by_incident(request, incident_id):
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


class IncidentViewSet(viewsets.ModelViewSet):
    queryset = Incident.objects.all()
    serializer_class = IncidentSerializer


class ComplianceViewSet(viewsets.ModelViewSet):
    queryset = Compliance.objects.all()
    serializer_class = ComplianceSerializer
    lookup_field = 'ComplianceId'

class RiskInstanceViewSet(viewsets.ModelViewSet):
    queryset = RiskInstance.objects.all()
    serializer_class = RiskInstanceSerializer
    
   
@api_view(['POST'])
def analyze_incident(request):
    """
    Analyzes an incident description using the SLM model and returns risk assessment data
    """
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

@api_view(['GET'])
def risk_metrics(request):
    """
    Get risk metrics with optional time filter
    """
    time_range = request.GET.get('timeRange', 'all')
    category = request.GET.get('category', 'all')
    priority = request.GET.get('priority', 'all')
    
    print(f"FILTER REQUEST: timeRange={time_range}, category={category}, priority={priority}")
    
    # Start with all risk instances
    queryset = RiskInstance.objects.all()
    print(f"Initial queryset count: {queryset.count()}")
    
    # Print columns and raw data for debugging
    print("Available columns:", [f.name for f in RiskInstance._meta.fields])
    
    # Sample data dump for debugging (first 5 records)
    print("Sample data:")
    for instance in queryset[:5]:
        print(f"ID: {instance.RiskInstanceId}, Category: {instance.Category}, Priority: {instance.RiskPriority}, Status: {instance.RiskStatus}")
    
    # Apply time filter if not 'all'
    if time_range != 'all':
        today = timezone.now().date()
        if time_range == '7days':
            start_date = today - timedelta(days=7)
        elif time_range == '30days':
            start_date = today - timedelta(days=30)
        elif time_range == '90days':
            start_date = today - timedelta(days=90)
        elif time_range == '1year':
            start_date = today - timedelta(days=365)
        else:
            start_date = None
            
        if start_date:
            queryset = queryset.filter(Date__gte=start_date)
            print(f"After time filter ({time_range}): {queryset.count()} records")
    
    # Apply category filter if not 'all'
    if category != 'all':
        # Handle the case conversion between frontend and backend naming
        category_map = {
            'operational': 'Operational',
            'financial': 'Financial',
            'strategic': 'Strategic', 
            'compliance': 'Compliance',
            'it-security': 'IT Security'
        }
        db_category = category_map.get(category, category)
        queryset = queryset.filter(Category__iexact=db_category)
        print(f"After category filter ({db_category}): {queryset.count()} records")
    
    # Apply priority filter if not 'all'
    if priority != 'all':
        # Handle the case conversion between frontend and backend naming
        priority_map = {
            'critical': 'Critical',
            'high': 'High',
            'medium': 'Medium',
            'low': 'Low'
        }
        db_priority = priority_map.get(priority, priority)
        queryset = queryset.filter(RiskPriority__iexact=db_priority)
        print(f"After priority filter ({db_priority}): {queryset.count()} records")
    
    # Calculate metrics
    total_risks = queryset.count()
    print(f"Final filtered count: {total_risks} records")
    
    # Accepted risks: Count risks with RiskStatus "Assigned" or "Approved"
    accepted_risks = queryset.filter(
        Q(RiskStatus__iexact='Assigned') | Q(RiskStatus__iexact='Approved')
    ).count()
    print(f"Accepted risks (Assigned or Approved): {accepted_risks}")
    
    # Rejected risks: Count risks with RiskStatus "Rejected"
    rejected_risks = queryset.filter(RiskStatus__iexact='Rejected').count()
    print(f"Rejected risks: {rejected_risks}")

    # Mitigated risks: Count rows with "Completed" in MitigationStatus
    mitigated_risks = 0
    in_progress_risks = 0
    
    # Print all distinct RiskStatus values to help debugging
    statuses = queryset.values_list('RiskStatus', flat=True).distinct()
    print(f"All RiskStatus values in filtered data: {list(statuses)}")
    
    try:
        # First try directly with ORM if MitigationStatus field exists
        if 'MitigationStatus' in [f.name for f in RiskInstance._meta.fields]:
            print("Trying ORM for MitigationStatus counts")
            mitigated_risks = queryset.filter(MitigationStatus='Completed').count()
            in_progress_risks = queryset.filter(MitigationStatus='Work in Progress').count()
            print(f"ORM counts - Mitigated: {mitigated_risks}, In Progress: {in_progress_risks}")
        
        # If that doesn't work or returns 0, try with direct SQL
        if mitigated_risks == 0 and in_progress_risks == 0:
            print("Trying direct SQL for MitigationStatus counts")
            with connection.cursor() as cursor:
                # First create a list of all the IDs from the queryset to use in our SQL
                risk_ids = list(queryset.values_list('RiskInstanceId', flat=True))
                
                if risk_ids:
                    # Convert the list to a comma-separated string for SQL
                    risk_ids_str = ','.join(map(str, risk_ids))
                    
                    # Check if MitigationStatus column exists
                    cursor.execute("SHOW COLUMNS FROM risk_instance LIKE 'MitigationStatus'")
                    mitigation_status_exists = cursor.fetchone() is not None
                    print(f"MitigationStatus column exists: {mitigation_status_exists}")
                    
                    if mitigation_status_exists:
                        # Count mitigated risks
                        sql = f"SELECT COUNT(*) FROM risk_instance WHERE RiskInstanceId IN ({risk_ids_str}) AND MitigationStatus = 'Completed'"
                        print(f"Executing SQL: {sql}")
                        cursor.execute(sql)
                        row = cursor.fetchone()
                        mitigated_risks = row[0] if row else 0
                        
                        # Count in-progress risks
                        sql = f"SELECT COUNT(*) FROM risk_instance WHERE RiskInstanceId IN ({risk_ids_str}) AND MitigationStatus = 'Work in Progress'"
                        print(f"Executing SQL: {sql}")
                        cursor.execute(sql)
                        row = cursor.fetchone()
                        in_progress_risks = row[0] if row else 0
                        
                        print(f"SQL counts - Mitigated: {mitigated_risks}, In Progress: {in_progress_risks}")
    except Exception as e:
        print(f"Error getting mitigated/in-progress risks: {e}")
    
    response_data = {
        'total': total_risks,
        'accepted': accepted_risks,
        'rejected': rejected_risks,
        'mitigated': mitigated_risks,
        'inProgress': in_progress_risks
    }
    print(f"Final response: {response_data}")
    
    return Response(response_data)

@api_view(['GET'])
def risk_metrics_by_category(request):
    category = request.GET.get('category', '')
    
    # Base queryset
    queryset = RiskInstance.objects.all()
    
    # Apply category filter if provided
    if category and category.lower() != 'all':
        queryset = queryset.filter(Category__icontains=category)
    
    # Count total filtered records
    total_count = queryset.count()
    
    # Get all statuses for these records
    all_statuses = list(queryset.values_list('RiskStatus', flat=True).distinct())
    print(f"All unique RiskStatus values for category '{category}': {all_statuses}")
    
    # Count by status
    open_count = 0
    in_progress_count = 0
    closed_count = 0
    
    # Status breakdown for detailed chart data
    status_breakdown = {}
    
    # Process each record
    for instance in queryset:
        status = instance.RiskStatus.lower() if instance.RiskStatus else ""
        
        # Count for summary metrics
        if status == "" or status is None:
            open_count += 1
            status_breakdown['Open'] = status_breakdown.get('Open', 0) + 1
        elif "open" in status:
            open_count += 1
            status_breakdown['Open'] = status_breakdown.get('Open', 0) + 1
        elif "progress" in status or "in prog" in status:
            in_progress_count += 1
            status_breakdown['In Progress'] = status_breakdown.get('In Progress', 0) + 1
        elif "closed" in status or "complete" in status:
            closed_count += 1
            status_breakdown['Closed'] = status_breakdown.get('Closed', 0) + 1
        else:
            # Any other status, count as open
            open_count += 1
            status_breakdown['Open'] = status_breakdown.get('Open', 0) + 1
    
    # Debug info
    print(f"Category '{category}': Total: {total_count}, Open: {open_count}, In Progress: {in_progress_count}, Closed: {closed_count}")
    
    return JsonResponse({
        'total': total_count,
        'open': open_count,
        'inProgress': in_progress_count,
        'closed': closed_count,
        'statusBreakdown': status_breakdown
    })

def generate_dates(days=30):
    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)
    return [start_date + timedelta(days=i) for i in range(days)]

@api_view(['GET'])
def risk_kpi_data(request):
    """Return all KPI data for the risk dashboard"""
    
    # Active Risks
    active_risks = random.randint(40, 60)
    
    # Risk Exposure
    risk_exposure = random.randint(800, 900)
    
    # Risk Recurrence
    risk_recurrence = random.randint(5, 8)
    
    # Risk Mitigation Completion Rate
    completion_rate = random.randint(65, 85)
    
    # Average Time to Remediate Critical Risks
    avg_remediation_time = random.randint(30, 45)
    
    # Rate of Recurrence
    recurrence_rate = round(random.uniform(5.5, 7.5), 1)
    
    # Average Time to Incident Response
    avg_response_time = random.randint(4, 8)
    
    # Cost of Mitigation
    mitigation_cost = random.randint(150, 200)
    
    # Risk Identification Rate
    identification_rate = random.randint(80, 95)
    
    # Due Mitigation Actions
    due_mitigation = random.randint(15, 30)
    
    # Risk Classification Accuracy
    classification_accuracy = random.randint(80, 95)
    
    # Risk Severity Distribution
    severity_levels = {
        'Critical': random.randint(5, 15),
        'High': random.randint(15, 25),
        'Medium': random.randint(30, 40),
        'Low': random.randint(20, 30)
    }
    
    # Risk Exposure Score
    exposure_score = random.randint(65, 85)
    
    # Risk Resilience
    resilience_hours = random.randint(4, 8)
    
    # Monthly trend data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    monthly_trend = [random.randint(30, 70) for _ in range(len(months))]
    
    # Risk Reduction Trend
    start_risks = random.randint(45, 60)
    new_risks = random.randint(10, 20)
    end_risks = start_risks + new_risks - random.randint(15, 25)
    
    return JsonResponse({
        'activeRisks': active_risks,
        'riskExposure': risk_exposure,
        'riskRecurrence': risk_recurrence,
        'mitigationCompletionRate': completion_rate,
        'avgRemediationTime': avg_remediation_time,
        'recurrenceRate': recurrence_rate,
        'avgResponseTime': avg_response_time,
        'mitigationCost': mitigation_cost,
        'identificationRate': identification_rate,
        'dueMitigation': due_mitigation,
        'classificationAccuracy': classification_accuracy,
        'severityLevels': severity_levels,
        'exposureScore': exposure_score,
        'resilienceHours': resilience_hours,
        'months': months,
        'monthlyTrend': monthly_trend,
        'riskReductionTrend': {
            'start': start_risks,
            'new': new_risks,
            'end': end_risks
        }
    })



@api_view(['GET'])
def risk_exposure_trend(request):
    """Return data for risk exposure trend over time using real database values"""
    print("==== RISK EXPOSURE TREND ENDPOINT CALLED ====")
    
    try:
        # Get optional parameters for flexibility
        months_count = int(request.GET.get('months', 6))  # Default to 6 months
        
        # Get the current total risk exposure (sum of all RiskExposureRating values)
        total_exposure = RiskInstance.objects.aggregate(
            total=models.Sum('RiskExposureRating')
        )['total'] or 0
        
        print(f"Current total risk exposure from database: {total_exposure}")
        
        # Generate monthly data for trend
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        months = []
        trend_data = []
        
        # Generate last N months dynamically and get real data for each month
        for i in range(months_count - 1, -1, -1):
            month_num = ((current_month - i - 1) % 12) + 1
            year = current_year if month_num <= current_month else current_year - 1
            month_name = datetime(year, month_num, 1).strftime('%b')
            months.append(month_name)
            
            # Start and end date for the month
            if month_num == 12:
                next_month = 1
                next_year = year + 1
            else:
                next_month = month_num + 1
                next_year = year
                
            start_date = datetime(year, month_num, 1).date()
            end_date = datetime(next_year, next_month, 1).date() - timedelta(days=1)
            
            # Query for risks in this month and sum their exposure ratings
            month_exposure = RiskInstance.objects.filter(
                Date__gte=start_date,
                Date__lte=end_date
            ).aggregate(
                total=models.Sum('RiskExposureRating')
            )['total'] or 0
            
            print(f"Month: {month_name}, Date range: {start_date} to {end_date}, Total exposure: {month_exposure}")
            trend_data.append(round(float(month_exposure), 1))
        
        # Current value is the total exposure
        current_value = round(float(total_exposure), 1)
        
        # Calculate percentage change from previous month
        if len(trend_data) >= 2 and trend_data[-2] > 0:
            percentage_change = round(((trend_data[-1] - trend_data[-2]) / trend_data[-2]) * 100, 1)
        else:
            percentage_change = 0
        
        print(f"Trend data: {trend_data}")
        print(f"Percentage change: {percentage_change}%")
        
        # Include min/max for charting
        min_value = min(trend_data) if trend_data else 0
        max_value = max(trend_data) if trend_data else 0
        
        response_data = {
            'current': current_value,
            'months': months,
            'trendData': trend_data,
            'percentageChange': percentage_change,
            'minValue': min_value,
            'maxValue': max_value,
            'range': max_value - min_value if trend_data else 0
        }
        
        print(f"Returning exposure trend data: {json.dumps(response_data)}")
        return JsonResponse(response_data)
    
    except Exception as e:
        print(f"ERROR in risk_exposure_trend: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return JsonResponse({
            'error': str(e),
            'current': 0,
            'months': [],
            'trendData': [],
            'percentageChange': 0,
            'minValue': 0,
            'maxValue': 0,
            'range': 0
        }, status=500)

@api_view(['GET'])
def risk_reduction_trend(request):
    print("==== RISK REDUCTION TREND ENDPOINT CALLED ====")
    
    try:
        period = request.GET.get('period', 'month')
        today = timezone.now().date()
        
        if period == 'month':
            current_start = today.replace(day=1)
            current_end = today
            
            if current_start.month == 1:
                prev_month = 12
                prev_year = current_start.year - 1
            else:
                prev_month = current_start.month - 1
                prev_year = current_start.year
            
            prev_start = datetime(prev_year, prev_month, 1).date()
            prev_end = current_start - timedelta(days=1)
        else:
            current_end = today
            current_start = today - timedelta(days=30)
            prev_end = current_start - timedelta(days=1)
            prev_start = prev_end - timedelta(days=30)
        
        print(f"Period: {period}")
        print(f"Current period: {current_start} to {current_end}")
        print(f"Previous period: {prev_start} to {prev_end}")
        
        start_exposure_query = RiskInstance.objects.filter(
            Date__lt=current_start
        ).exclude(
            MitigationStatus__iexact='Completed',
            MitigationCompletedDate__lt=current_start
        ).aggregate(total=models.Sum('RiskExposureRating'))
        
        start_exposure = float(start_exposure_query['total'] or 0)
        print(f"Exposure at start: {start_exposure}")
        
        new_exposure_query = RiskInstance.objects.filter(
            Date__gte=current_start,
            Date__lte=current_end
        ).aggregate(total=models.Sum('RiskExposureRating'))
        
        new_exposure = float(new_exposure_query['total'] or 0)
        print(f"New exposure: {new_exposure}")
        
        mitigated_exposure_query = RiskInstance.objects.filter(
            MitigationCompletedDate__gte=current_start,
            MitigationCompletedDate__lte=current_end,
            MitigationStatus__iexact='Completed'
        ).aggregate(total=models.Sum('RiskExposureRating'))
        
        mitigated_exposure = float(mitigated_exposure_query['total'] or 0)
        print(f"Mitigated exposure: {mitigated_exposure}")
        
        end_exposure_query = RiskInstance.objects.filter(
            Date__lte=current_end
        ).exclude(
            MitigationStatus__iexact='Completed',
            MitigationCompletedDate__lte=current_end
        ).aggregate(total=models.Sum('RiskExposureRating'))
        
        end_exposure = float(end_exposure_query['total'] or 0)
        print(f"Exposure at end: {end_exposure}")
        
        total_initial_exposure = start_exposure + new_exposure
        
        if total_initial_exposure > 0:
            reduction_percentage = round(((total_initial_exposure - end_exposure) / total_initial_exposure) * 100, 1)
        else:
            reduction_percentage = 0
        
        if reduction_percentage < 0:
            reduction_percentage = 0
        
        print(f"Reduction percentage: {reduction_percentage}%")
        
        response_data = {
            'startCount': round(start_exposure),
            'newCount': round(new_exposure),
            'mitigatedCount': round(mitigated_exposure),
            'endCount': round(end_exposure),
            'reductionPercentage': reduction_percentage
        }
        
        print(f"Returning risk reduction trend data: {json.dumps(response_data)}")
        return JsonResponse(response_data)
    
    except Exception as e:
        print(f"ERROR in risk_reduction_trend: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return JsonResponse({
            'error': str(e),
            'startCount': 45,
            'newCount': 15,
            'mitigatedCount': 25,
            'endCount': 35,
            'reductionPercentage': 25.0
        }, status=500)

@api_view(['GET'])
def high_criticality_risks(request):
    """Return data for high criticality risks from the database"""
    print("==== HIGH CRITICALITY RISKS ENDPOINT CALLED ====")
    
    try:
        # Get count of high criticality risks
        high_count = RiskInstance.objects.filter(Criticality__iexact='High').count()
        
        # Get count of critical criticality risks
        critical_count = RiskInstance.objects.filter(Criticality__iexact='Critical').count()
        
        # Total high criticality risks
        total_count = high_count + critical_count
        
        print(f"Found {high_count} High criticality risks")
        print(f"Found {critical_count} Critical criticality risks")
        print(f"Total high criticality risks: {total_count}")
        
        # Calculate percentage of total risks
        total_risks = RiskInstance.objects.count()
        percentage = round((total_count / total_risks) * 100, 1) if total_risks > 0 else 0
        
        print(f"Percentage of total risks: {percentage}% ({total_count}/{total_risks})")
        
        # Generate trend data for the last 6 months
        months = []
        trend_data = []
        
        # Generate monthly labels
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        for i in range(5, -1, -1):
            month_num = ((current_month - i - 1) % 12) + 1
            year = current_year if month_num <= current_month else current_year - 1
            month_name = datetime(year, month_num, 1).strftime('%b')
            months.append(month_name)
            
            # Start and end date for the month
            if month_num == 12:
                next_month = 1
                next_year = year + 1
            else:
                next_month = month_num + 1
                next_year = year
                
            start_date = datetime(year, month_num, 1).date()
            end_date = datetime(next_year, next_month, 1).date() - timedelta(days=1)
            
            # Query for high criticality risks in this month
            month_high_count = RiskInstance.objects.filter(
                Criticality__iexact='High',
                Date__gte=start_date,
                Date__lte=end_date
            ).count()
            
            month_critical_count = RiskInstance.objects.filter(
                Criticality__iexact='Critical',
                Date__gte=start_date,
                Date__lte=end_date
            ).count()
            
            month_total = month_high_count + month_critical_count
            
            print(f"Month: {month_name}, Date range: {start_date} to {end_date}, High: {month_high_count}, Critical: {month_critical_count}, Total: {month_total}")
            trend_data.append(month_total)
        
        response_data = {
            'count': total_count,
            'highCount': high_count,
            'criticalCount': critical_count,
            'percentage': percentage,
            'months': months,
            'trendData': trend_data
        }
        
        print(f"Returning high criticality risks data: {json.dumps(response_data)}")
        return JsonResponse(response_data)
    
    except Exception as e:
        print(f"ERROR in high_criticality_risks: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return JsonResponse({
            'error': str(e),
            'count': 0,
            'highCount': 0,
            'criticalCount': 0,
            'percentage': 0,
            'months': [],
            'trendData': []
        }, status=500)

@api_view(['GET'])
def risk_identification_rate(request):
    """
    Calculate the risk identification rate (number of new risks identified per period)
    """
    print("==== RISK IDENTIFICATION RATE ENDPOINT CALLED ====")
    
    try:
        # Get optional filter parameters
        time_range = request.GET.get('timeRange', '6months')  # Default to last 6 months
        category = request.GET.get('category', 'all')
        
        # Define the time period to analyze
        today = timezone.now().date()
        if time_range == '30days':
            start_date = today - timedelta(days=30)
            period_length = 30
        elif time_range == '90days':
            start_date = today - timedelta(days=90)
            period_length = 90
        elif time_range == '6months':
            start_date = today - timedelta(days=180)
            period_length = 180
        elif time_range == '1year':
            start_date = today - timedelta(days=365)
            period_length = 365
        else:
            # Default to 6 months
            start_date = today - timedelta(days=180)
            period_length = 180
        
        print(f"Analyzing risk identification from {start_date} to {today}")
        
        # Base queryset - risks created in the specified period
        queryset = RiskInstance.objects.filter(Date__gte=start_date, Date__lte=today)
        
        # Apply category filter if specified
        if category and category.lower() != 'all':
            category_map = {
                'operational': 'Operational',
                'financial': 'Financial',
                'strategic': 'Strategic', 
                'compliance': 'Compliance',
                'it-security': 'IT Security'
            }
            db_category = category_map.get(category.lower(), category)
            queryset = queryset.filter(Category__iexact=db_category)
            print(f"Applied category filter: {db_category}, records: {queryset.count()}")
        
        # Count total risks identified in the period
        total_risks = queryset.count()
        print(f"Total risks identified in period: {total_risks}")
        
        # Calculate daily average rate
        daily_average = round(total_risks / period_length, 1)
        print(f"Daily average identification rate: {daily_average} risks/day")
        
        # Generate monthly data for trend chart (last 6 months)
        months = []
        trend_data = []
        
        # Start from 6 months ago and move forward
        for i in range(5, -1, -1):
            # Calculate month start and end dates
            month_end = today.replace(day=1) - timedelta(days=1) if i == 0 else (
                today.replace(day=1) - timedelta(days=1) - relativedelta(months=i-1)
            )
            month_start = month_end.replace(day=1)
            
            # Get month name for display
            month_name = month_start.strftime('%b')
            months.append(month_name)
            
            # Count risks identified in this month
            month_count = queryset.filter(Date__gte=month_start, Date__lte=month_end).count()
            
            # Calculate days in month to normalize the rate
            days_in_month = (month_end - month_start).days + 1
            
            # Calculate identification rate as percentage of total risks that could be identified
            # (using a baseline of expected risks per month, e.g., 30 risks per month is 100%)
            baseline_risks_per_month = 30  # This can be adjusted based on organizational benchmarks
            identification_rate = min(100, round((month_count / baseline_risks_per_month) * 100))
            
            trend_data.append(identification_rate)
            print(f"Month: {month_name}, Risks identified: {month_count}, Rate: {identification_rate}%")
        
        # Calculate current month's rate for the main KPI value
        current_month_start = today.replace(day=1)
        current_month_count = queryset.filter(Date__gte=current_month_start, Date__lte=today).count()
        current_month_rate = min(100, round((current_month_count / baseline_risks_per_month) * 100))
        
        # Calculate percentage change from previous month
        if len(trend_data) >= 2:
            percentage_change = round(((trend_data[-1] - trend_data[-2]) / trend_data[-2]) * 100, 1) if trend_data[-2] > 0 else 0
        else:
            percentage_change = 0
        
        print(f"Current month rate: {current_month_rate}%, Change from previous month: {percentage_change}%")
        
        # Find min and max values for chart scaling
        min_value = min(trend_data) if trend_data else 0
        max_value = max(trend_data) if trend_data else 100
        
        # Prepare response data
        response_data = {
            'current': current_month_rate,
            'dailyAverage': daily_average,
            'percentageChange': percentage_change,
            'trendData': trend_data,
            'months': months,
            'minValue': min_value,
            'maxValue': max_value,
            'totalRisksIdentified': total_risks,
            'period': time_range
        }
        
        print(f"Returning risk identification rate data: {json.dumps(response_data)}")
        return JsonResponse(response_data)
    
    except Exception as e:
        import traceback
        print(f"ERROR in risk_identification_rate: {str(e)}")
        print(traceback.format_exc())
        
        # Return fallback data in case of error
        return JsonResponse({
            'error': str(e),
            'current': 88,
            'dailyAverage': 4.2,
            'percentageChange': 3.5,
            'trendData': [75, 82, 88, 92, 85, 88],
            'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'minValue': 75,
            'maxValue': 92,
            'totalRisksIdentified': 750,
            'period': '6months'
        }, status=500)

@api_view(['GET'])
def due_mitigation(request):
    """
    Calculate percentage of mitigation tasks that are past due date and incomplete
    by analyzing the RiskInstance table
    """
    print("==== DUE MITIGATION ENDPOINT CALLED ====")
    
    try:
        # Get optional filters
        time_range = request.GET.get('timeRange', 'all')
        category = request.GET.get('category', 'all')
        
        # Base queryset - only include risks with mitigation data
        queryset = RiskInstance.objects.filter(
            MitigationDueDate__isnull=False
        )
        
        # Apply time filter if not 'all'
        if time_range != 'all':
            today = timezone.now().date()
            if time_range == '30days':
                start_date = today - timedelta(days=30)
            elif time_range == '90days':
                start_date = today - timedelta(days=90)
            elif time_range == '6months':
                start_date = today - timedelta(days=180)
            elif time_range == '1year':
                start_date = today - timedelta(days=365)
            else:
                start_date = today - timedelta(days=30)  # Default to last 30 days
                
            queryset = queryset.filter(Date__gte=start_date)
            print(f"Applied time filter: {time_range}, records: {queryset.count()}")
        
        # Apply category filter if specified
        if category and category.lower() != 'all':
            category_map = {
                'operational': 'Operational',
                'financial': 'Financial',
                'strategic': 'Strategic', 
                'compliance': 'Compliance',
                'it-security': 'IT Security'
            }
            db_category = category_map.get(category.lower(), category)
            queryset = queryset.filter(Category__iexact=db_category)
            print(f"Applied category filter: {db_category}, records: {queryset.count()}")
        
        # Get today's date for comparison
        today = timezone.now().date()
        
        # Total mitigation tasks
        total_count = queryset.count()
        print(f"Total mitigation tasks: {total_count}")
        
        # Completed tasks (MitigationStatus = 'Completed')
        completed_tasks = queryset.filter(MitigationStatus='Completed')
        completed_count = completed_tasks.count()
        completed_percentage = round((completed_count / total_count) * 100) if total_count > 0 else 0
        print(f"Completed tasks: {completed_count} ({completed_percentage}%)")
        
        # Overdue tasks (MitigationDueDate < today AND MitigationStatus != 'Completed')
        overdue_tasks = queryset.filter(
            MitigationDueDate__lt=today
        ).exclude(
            MitigationStatus='Completed'
        )
        overdue_count = overdue_tasks.count()
        overdue_percentage = round((overdue_count / total_count) * 100) if total_count > 0 else 0
        print(f"Overdue tasks: {overdue_count} ({overdue_percentage}%)")
        
        # Pending tasks (neither completed nor overdue)
        pending_count = total_count - completed_count - overdue_count
        pending_percentage = 100 - completed_percentage - overdue_percentage
        print(f"Pending tasks: {pending_count} ({pending_percentage}%)")
        
        # Get the previous period data for percentage change calculation
        # For simplicity, we'll compare with data from the previous equal time period
        prev_period_end = None
        prev_period_start = None
        
        if time_range == '30days':
            prev_period_end = today - timedelta(days=30)
            prev_period_start = prev_period_end - timedelta(days=30)
        elif time_range == '90days':
            prev_period_end = today - timedelta(days=90)
            prev_period_start = prev_period_end - timedelta(days=90)
        elif time_range == '6months':
            prev_period_end = today - timedelta(days=180)
            prev_period_start = prev_period_end - timedelta(days=180)
        elif time_range == '1year':
            prev_period_end = today - timedelta(days=365)
            prev_period_start = prev_period_end - timedelta(days=365)
        else:
            # Default to previous 30 days
            prev_period_end = today - timedelta(days=30)
            prev_period_start = prev_period_end - timedelta(days=30)
        
        # Calculate previous period's overdue percentage
        prev_queryset = RiskInstance.objects.filter(
            MitigationDueDate__isnull=False,
            Date__gte=prev_period_start,
            Date__lte=prev_period_end
        )
        
        if category and category.lower() != 'all':
            prev_queryset = prev_queryset.filter(Category__iexact=db_category)
        
        prev_total = prev_queryset.count()
        
        prev_overdue_count = prev_queryset.filter(
            MitigationDueDate__lt=prev_period_end
        ).exclude(
            MitigationStatus='Completed'
        ).count()
        
        prev_overdue_percentage = round((prev_overdue_count / prev_total) * 100) if prev_total > 0 else 0
        print(f"Previous period overdue: {prev_overdue_count}/{prev_total} ({prev_overdue_percentage}%)")
        
        # Calculate percentage change
        percentage_change = overdue_percentage - prev_overdue_percentage
        print(f"Percentage change: {percentage_change}%")
        
        # Return the response
        return Response({
            'overduePercentage': overdue_percentage,
            'completedPercentage': completed_percentage,
            'pendingPercentage': pending_percentage,
            'overdueCount': overdue_count,
            'completedCount': completed_count,
            'pendingCount': pending_count,
            'totalCount': total_count,
            'percentageChange': percentage_change
        })
        
    except Exception as e:
        import traceback
        print(f"ERROR in due_mitigation: {str(e)}")
        print(traceback.format_exc())
        
        # Return fallback data in case of error
        return Response({
            'error': str(e),
            'overduePercentage': 22,
            'completedPercentage': 50,
            'pendingPercentage': 28,
            'overdueCount': 8,
            'completedCount': 18,
            'pendingCount': 10,
            'totalCount': 36,
            'percentageChange': 2.8
        }, status=500)

@api_view(['GET'])
def classification_accuracy(request):
    """Return data for risk classification accuracy"""
    
    # In a real implementation, this would query your database for risk classification data
    # For demonstration, we'll generate realistic sample data
    
    # Overall accuracy
    accuracy = random.randint(85, 92)
    
    # Accuracy by category
    category_accuracy = {
        'Compliance': random.randint(85, 95),
        'Operational': random.randint(82, 90),
        'Security': random.randint(80, 93),
        'Financial': random.randint(85, 92)
    }
    
    # Time series data
    time_series_data = []
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    
    # Generate realistic time series with a slight upward trend
    base_value = random.randint(80, 85)
    for i, month in enumerate(months):
        # Small improvement over time with some variation
        trend_value = base_value + (i * random.uniform(0.5, 1.5))
        variation = random.uniform(-1.5, 1.5)
        value = round(min(95, max(80, trend_value + variation)))
        
        time_series_data.append({
            'month': month,
            'value': value
        })
    
    # Calculate percentage change from previous month
    current = time_series_data[-1]['value']
    previous = time_series_data[-2]['value']
    percentage_change = round(((current - previous) / previous) * 100, 1) if previous else 0
    
    return Response({
        'accuracy': accuracy,
        'percentageChange': percentage_change,
        'categoryAccuracy': category_accuracy,
        'timeSeriesData': time_series_data
    })

@api_view(['GET'])
def improvement_initiatives(request):
    """Return data for completion of improvement initiatives"""
    
    # In a real implementation, this would query your improvement_initiatives table
    # For demonstration, we'll generate realistic sample data
    
    # Completion percentage
    completion_percentage = random.randint(70, 85)
    
    # Total initiatives
    total_count = random.randint(25, 40)
    
    # Calculate counts
    completed_count = int(total_count * completion_percentage / 100)
    pending_count = total_count - completed_count
    
    # Breakdown by category (optional)
    category_breakdown = {
        'Security': {
            'total': random.randint(8, 15),
            'completed': random.randint(5, 10)
        },
        'Compliance': {
            'total': random.randint(6, 12),
            'completed': random.randint(4, 8)
        },
        'Process': {
            'total': random.randint(7, 14),
            'completed': random.randint(5, 10)
        }
    }
    
    return Response({
        'completionPercentage': completion_percentage,
        'totalCount': total_count,
        'completedCount': completed_count,
        'pendingCount': pending_count,
        'categoryBreakdown': category_breakdown
    })

@api_view(['GET'])
def risk_impact(request):
    """Return data for risk impact on operations and finances"""
    
    # In a real implementation, this would query your database for risk impact data
    # For demonstration, we'll generate realistic sample data
    
    # Overall risk impact score (average of operational and financial impacts)
    overall_score = random.randint(55, 75) / 10  # Scale to 5.5-7.5 out of 10
    
    # Impact distribution
    impact_distribution = {
        'operational': {
            'low': random.randint(10, 20),
            'medium': random.randint(25, 35),
            'high': random.randint(15, 25),
            'critical': random.randint(5, 15)
        },
        'financial': {
            'low': random.randint(15, 25),     # < ₹100K
            'medium': random.randint(20, 30),  # ₹100K-₹1M
            'high': random.randint(15, 25),    # ₹1M-₹10M
            'critical': random.randint(5, 15)  # > ₹10M
        }
    }
    
    # Top impact risks
    top_risks = [
        {
            'id': 1,
            'title': 'Service Outage',
            'operational_impact': 8.5,
            'financial_impact': 9.2,
            'category': 'Operational'
        },
        {
            'id': 2,
            'title': 'Data Breach',
            'operational_impact': 7.2,
            'financial_impact': 9.5,
            'category': 'Security'
        },
        {
            'id': 3,
            'title': 'Compliance Violation',
            'operational_impact': 6.8,
            'financial_impact': 8.1,
            'category': 'Compliance'
        },
        {
            'id': 4,
            'title': 'Supply Chain Disruption',
            'operational_impact': 9.1,
            'financial_impact': 7.4,
            'category': 'Operational'
        },
        {
            'id': 5,
            'title': 'Market Volatility',
            'operational_impact': 5.6,
            'financial_impact': 8.7,
            'category': 'Financial'
        }
    ]
    
    return Response({
        'overallScore': overall_score,
        'impactDistribution': impact_distribution,
        'topRisks': top_risks
    })

@api_view(['GET'])
def risk_severity(request):
    """Return data for risk severity based on potential consequences"""
    print("==== RISK SEVERITY ENDPOINT CALLED ====")
    
    try:
        # Get optional filters
        time_range = request.GET.get('timeRange', 'all')
        category = request.GET.get('category', 'all')
        
        # Check if database has any data
        risk_count = RiskInstance.objects.count()
        print(f"Total risk count in database: {risk_count}")
        
        # Base queryset
        queryset = RiskInstance.objects.all()
        
        # Apply time filter if specified
        if time_range != 'all':
            today = timezone.now().date()
            if time_range == '30days':
                start_date = today - timedelta(days=30)
            elif time_range == '90days':
                start_date = today - timedelta(days=90)
            elif time_range == '6months':
                start_date = today - timedelta(days=180)
            elif time_range == '1year':
                start_date = today - timedelta(days=365)
            else:
                start_date = today - timedelta(days=30)  # Default to last 30 days
                
            queryset = queryset.filter(Date__gte=start_date)
            print(f"Applied time filter: {time_range}, records: {queryset.count()}")
        
        # Apply category filter if specified
        if category and category.lower() != 'all':
            category_map = {
                'operational': 'Operational',
                'financial': 'Financial',
                'strategic': 'Strategic', 
                'compliance': 'Compliance',
                'it-security': 'IT Security'
            }
            db_category = category_map.get(category.lower(), category)
            queryset = queryset.filter(Category__iexact=db_category)
            print(f"Applied category filter: {db_category}, records: {queryset.count()}")
        
        # If no data found, use default values
        if queryset.count() == 0:
            print("No data found, using default values")
            return Response({
                'severityDistribution': {
                    'Low': 20,
                    'Medium': 40,
                    'High': 25,
                    'Critical': 15
                },
                'severityPercentages': {
                    'Low': 20,
                    'Medium': 40,
                    'High': 25,
                    'Critical': 15
                },
                'averageSeverity': 6.8,
                'trendData': [
                    {'month': 'Jan', 'Low': 15, 'Medium': 30, 'High': 20, 'Critical': 10},
                    {'month': 'Feb', 'Low': 18, 'Medium': 32, 'High': 22, 'Critical': 12},
                    {'month': 'Mar', 'Low': 16, 'Medium': 35, 'High': 24, 'Critical': 14},
                    {'month': 'Apr', 'Low': 20, 'Medium': 33, 'High': 21, 'Critical': 11},
                    {'month': 'May', 'Low': 19, 'Medium': 36, 'High': 23, 'Critical': 13},
                    {'month': 'Jun', 'Low': 20, 'Medium': 40, 'High': 25, 'Critical': 15}
                ],
                'topSevereRisks': [
                    {'id': 1, 'title': 'Data Center Failure', 'severity': 9.5, 'category': 'Infrastructure'},
                    {'id': 2, 'title': 'Critical Data Breach', 'severity': 9.2, 'category': 'Security'},
                    {'id': 3, 'title': 'Regulatory Non-Compliance', 'severity': 8.7, 'category': 'Compliance'},
                    {'id': 4, 'title': 'Key Supplier Failure', 'severity': 8.4, 'category': 'Supply Chain'},
                    {'id': 5, 'title': 'Critical System Outage', 'severity': 8.1, 'category': 'Technology'}
                ]
            })
        
        # Count risks by criticality (severity distribution)
        severity_distribution = {
            'Low': queryset.filter(Criticality__iexact='Low').count(),
            'Medium': queryset.filter(Criticality__iexact='Medium').count(),
            'High': queryset.filter(Criticality__iexact='High').count(),
            'Critical': queryset.filter(Criticality__iexact='Critical').count()
        }
        
        # If we have no data in any category, use defaults
        if sum(severity_distribution.values()) == 0:
            severity_distribution = {
                'Low': 20,
                'Medium': 40,
                'High': 25,
                'Critical': 15
            }
        
        # Calculate total for percentages
        total = sum(severity_distribution.values())
        severity_percentages = {
            category: round((count / total) * 100) if total > 0 else 0
            for category, count in severity_distribution.items()
        }
        
        print(f"Severity distribution: {severity_distribution}")
        print(f"Severity percentages: {severity_percentages}")
        
        # Calculate average severity score (1-10 scale) based on RiskImpact
        try:
            avg_impact = queryset.aggregate(avg=models.Avg('RiskImpact'))['avg'] or 0
            average_severity = round(float(avg_impact), 1)
        except:
            # If conversion fails, use default value
            average_severity = 6.8
        
        print(f"Average severity score: {average_severity}")
        
        # Generate monthly trend data for severity distribution
        months = []
        trend_data = []
        
        # Current date for reference
        today = timezone.now().date()
        
        # Generate data for the last 6 months
        for i in range(5, -1, -1):
            month_end = today.replace(day=1) - timedelta(days=1) if i == 0 else (
                today.replace(day=1) - timedelta(days=1) - relativedelta(months=i-1)
            )
            month_start = month_end.replace(day=1)
            
            month_name = month_start.strftime('%b')
            months.append(month_name)
            
            # Get counts for each criticality level in this month
            month_qs = queryset.filter(Date__gte=month_start, Date__lte=month_end)
            
            month_data = {
                'month': month_name,
                'Low': month_qs.filter(Criticality__iexact='Low').count(),
                'Medium': month_qs.filter(Criticality__iexact='Medium').count(),
                'High': month_qs.filter(Criticality__iexact='High').count(),
                'Critical': month_qs.filter(Criticality__iexact='Critical').count()
            }
            
            trend_data.append(month_data)
            print(f"Month: {month_name}, Data: {month_data}")
        
        # Get top severe risks (based on highest RiskImpact)
        top_severe_risks = []
        top_risks = queryset.order_by('-RiskImpact')[:5]
        
        for risk in top_risks:
            title = risk.RiskDescription if risk.RiskDescription else f"Risk {risk.RiskInstanceId}"
            # Truncate long titles
            if title and len(title) > 50:
                title = title[:47] + '...'
                
            # Safely convert RiskImpact to float
            try:
                severity = float(risk.RiskImpact) if risk.RiskImpact is not None else 0
            except (ValueError, TypeError):
                severity = 0
                
            top_severe_risks.append({
                'id': risk.RiskInstanceId,
                'title': title,
                'severity': severity,
                'category': risk.Category or 'Uncategorized'
            })
        
        # If no top risks found, use default values
        if len(top_severe_risks) == 0:
            top_severe_risks = [
                {'id': 1, 'title': 'Data Center Failure', 'severity': 9.5, 'category': 'Infrastructure'},
                {'id': 2, 'title': 'Critical Data Breach', 'severity': 9.2, 'category': 'Security'},
                {'id': 3, 'title': 'Regulatory Non-Compliance', 'severity': 8.7, 'category': 'Compliance'},
                {'id': 4, 'title': 'Key Supplier Failure', 'severity': 8.4, 'category': 'Supply Chain'},
                {'id': 5, 'title': 'Critical System Outage', 'severity': 8.1, 'category': 'Technology'}
            ]
        
        print(f"Top severe risks: {top_severe_risks}")
        
        # Return response data
        return Response({
            'severityDistribution': severity_distribution,
            'severityPercentages': severity_percentages,
            'averageSeverity': average_severity,
            'trendData': trend_data,
            'topSevereRisks': top_severe_risks
        })
        
    except Exception as e:
        import traceback
        print(f"ERROR in risk_severity: {str(e)}")
        print(traceback.format_exc())
        
        # Return fallback data in case of error
        return Response({
            'error': str(e),
            'severityDistribution': {
                'Low': 20,
                'Medium': 40,
                'High': 25,
                'Critical': 15
            },
            'severityPercentages': {
                'Low': 20,
                'Medium': 40,
                'High': 25,
                'Critical': 15
            },
            'averageSeverity': 6.8,
            'trendData': [
                {'month': 'Jan', 'Low': 15, 'Medium': 30, 'High': 20, 'Critical': 10},
                {'month': 'Feb', 'Low': 18, 'Medium': 32, 'High': 22, 'Critical': 12},
                {'month': 'Mar', 'Low': 16, 'Medium': 35, 'High': 24, 'Critical': 14},
                {'month': 'Apr', 'Low': 20, 'Medium': 33, 'High': 21, 'Critical': 11},
                {'month': 'May', 'Low': 19, 'Medium': 36, 'High': 23, 'Critical': 13},
                {'month': 'Jun', 'Low': 20, 'Medium': 40, 'High': 25, 'Critical': 15}
            ],
            'topSevereRisks': [
                {'id': 1, 'title': 'Data Center Failure', 'severity': 9.5, 'category': 'Infrastructure'},
                {'id': 2, 'title': 'Critical Data Breach', 'severity': 9.2, 'category': 'Security'},
                {'id': 3, 'title': 'Regulatory Non-Compliance', 'severity': 8.7, 'category': 'Compliance'},
                {'id': 4, 'title': 'Key Supplier Failure', 'severity': 8.4, 'category': 'Supply Chain'},
                {'id': 5, 'title': 'Critical System Outage', 'severity': 8.1, 'category': 'Technology'}
            ]
        }, status=200)  # Return 200 OK even for fallback data

@api_view(['GET'])
def risk_exposure_score(request):
    """Return data for risk exposure score"""
    
    # In a real implementation, this would query your database for risk exposure data
    # For demonstration, we'll generate realistic sample data
    
    # Overall exposure score (percentage)
    overall_score = random.randint(70, 80)
    
    # Generate risk exposure data points
    risk_points = [
        {
            'id': 1,
            'title': 'Data Center Outage',
            'impact': random.uniform(7.5, 9.5),
            'likelihood': random.uniform(5.5, 8.5),
            'category': 'Infrastructure',
            'exposure': None  # Will calculate below
        },
        {
            'id': 2,
            'title': 'Sensitive Data Breach',
            'impact': random.uniform(8.0, 9.5),
            'likelihood': random.uniform(5.0, 7.5),
            'category': 'Security',
            'exposure': None
        },
        {
            'id': 3,
            'title': 'Regulatory Non-Compliance',
            'impact': random.uniform(7.0, 9.0),
            'likelihood': random.uniform(4.0, 6.5),
            'category': 'Compliance',
            'exposure': None
        },
        {
            'id': 4,
            'title': 'Critical System Failure',
            'impact': random.uniform(7.5, 9.0),
            'likelihood': random.uniform(4.0, 7.0),
            'category': 'Technology',
            'exposure': None
        },
        {
            'id': 5,
            'title': 'Supply Chain Disruption',
            'impact': random.uniform(6.5, 8.5),
            'likelihood': random.uniform(5.0, 7.5),
            'category': 'Operational',
            'exposure': None
        },
        {
            'id': 6,
            'title': 'Financial Fraud',
            'impact': random.uniform(7.0, 8.5),
            'likelihood': random.uniform(3.0, 5.5),
            'category': 'Financial',
            'exposure': None
        },
        {
            'id': 7,
            'title': 'Market Volatility',
            'impact': random.uniform(5.5, 7.5),
            'likelihood': random.uniform(6.0, 8.0),
            'category': 'Financial',
            'exposure': None
        },
        {
            'id': 8,
            'title': 'Key Personnel Departure',
            'impact': random.uniform(5.0, 7.0),
            'likelihood': random.uniform(4.0, 6.5),
            'category': 'HR',
            'exposure': None
        }
    ]
    
    # Calculate exposure scores and add colors
    for risk in risk_points:
        risk['exposure'] = round(risk['impact'] * risk['likelihood'] / 10, 1)  # Scale to 0-10
    
    # Sort by exposure score (highest to lowest)
    risk_points.sort(key=lambda x: x['exposure'], reverse=True)
    
    # Category distribution
    category_distribution = {}
    for risk in risk_points:
        category = risk['category']
        if category in category_distribution:
            category_distribution[category] += 1
        else:
            category_distribution[category] = 1
    
    return Response({
        'overallScore': overall_score,
        'riskPoints': risk_points,
        'categoryDistribution': category_distribution
    })

@api_view(['GET'])
def risk_resilience(request):
    """Return data for risk resilience to absorb shocks"""
    
    # In a real implementation, this would query your database for resilience test data
    # For demonstration, we'll generate realistic sample data
    
    # Average resilience metrics
    avg_downtime = random.randint(3, 7)  # hours
    avg_recovery = random.randint(4, 8)  # hours
    
    # Resilience by risk category
    category_data = [
        {
            'category': 'Infrastructure',
            'downtime': random.randint(4, 8),
            'recovery': random.randint(5, 9)
        },
        {
            'category': 'Application',
            'downtime': random.randint(2, 5),
            'recovery': random.randint(3, 6)
        },
        {
            'category': 'Network',
            'downtime': random.randint(3, 7),
            'recovery': random.randint(4, 8)
        },
        {
            'category': 'Security',
            'downtime': random.randint(5, 9),
            'recovery': random.randint(6, 10)
        }
    ]
    
    # Historical trend data
    trend_data = []
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    
    for month in months:
        trend_data.append({
            'month': month,
            'downtime': random.randint(3, 8),
            'recovery': random.randint(4, 9)
        })
    
    return Response({
        'avgDowntime': avg_downtime,
        'avgRecovery': avg_recovery,
        'categoryData': category_data,
        'trendData': trend_data,
        'months': months
    })

@api_view(['GET'])
def risk_assessment_frequency(request):
    """Return data for frequency of risk assessment review"""
    
    # In a real implementation, this would query your database for risk review data
    # For demonstration, we'll generate realistic sample data
    
    # Average review frequency in days
    avg_review_frequency = random.randint(45, 75)  # days
    
    # Review frequency by risk category
    category_frequencies = {
        'Security': random.randint(30, 60),
        'Operational': random.randint(40, 70),
        'Compliance': random.randint(20, 45),
        'Financial': random.randint(50, 80),
        'Strategic': random.randint(60, 90)
    }
    
    # Most frequently reviewed risks
    most_reviewed = [
        {'id': 1, 'title': 'Data Breach', 'reviews': random.randint(5, 8), 'last_review': '2023-06-10', 'category': 'Security'},
        {'id': 2, 'title': 'Regulatory Non-Compliance', 'reviews': random.randint(4, 7), 'last_review': '2023-06-05', 'category': 'Compliance'},
        {'id': 3, 'title': 'System Outage', 'reviews': random.randint(3, 6), 'last_review': '2023-05-28', 'category': 'Operational'},
        {'id': 4, 'title': 'Supply Chain Disruption', 'reviews': random.randint(3, 5), 'last_review': '2023-05-15', 'category': 'Operational'},
        {'id': 5, 'title': 'Financial Reporting Error', 'reviews': random.randint(2, 4), 'last_review': '2023-05-10', 'category': 'Financial'}
    ]
    
    # Overdue reviews
    overdue_reviews = [
        {'id': 6, 'title': 'Market Volatility', 'last_review': '2023-03-10', 'days_overdue': random.randint(30, 60), 'category': 'Financial'},
        {'id': 7, 'title': 'Talent Shortage', 'last_review': '2023-02-15', 'days_overdue': random.randint(40, 70), 'category': 'Strategic'},
        {'id': 8, 'title': 'Legacy System Failure', 'last_review': '2023-04-05', 'days_overdue': random.randint(20, 40), 'category': 'Technology'}
    ]
    
    # Monthly review counts
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    monthly_reviews = [random.randint(10, 25) for _ in months]
    
    return Response({
        'avgReviewFrequency': avg_review_frequency,
        'categoryFrequencies': category_frequencies,
        'mostReviewed': most_reviewed,
        'overdueReviews': overdue_reviews,
        'months': months,
        'monthlyReviews': monthly_reviews,
        'overdueCount': len(overdue_reviews),
        'totalRisks': random.randint(50, 80)
    })

@api_view(['GET'])
def risk_approval_rate_cycle(request):
    """
    Return data for risk approval rate and review cycles
    
    Returns:
      - approvalRate: Percentage of risks approved
      - avgReviewCycles: Average number of review cycles per risk 
      - maxReviewCycles: Maximum review cycles among all risks
    """
    print("==== RISK APPROVAL RATE CYCLE ENDPOINT CALLED ====")
    
    try:
        # Use the SQL query logic from get_risk_approval_metrics
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT 
                    ROUND(
                        (SUM(CASE WHEN RiskStatus = 'Approved' THEN 1 ELSE 0 END) * 100.0) / COUNT(*)
                    ) AS approval_rate_percent,
                    ROUND(AVG(ReviewerCount), 1) AS avg_review_cycles,
                    MAX(ReviewerCount) AS max_review_cycles
                FROM risk_instance
                WHERE ReviewerCount IS NOT NULL;
            """)
            row = cursor.fetchone()
            
            approval_rate = row[0] if row and row[0] is not None else 0
            avg_review_cycles = float(row[1]) if row and row[1] is not None else 3.2
            max_review_cycles = row[2] if row and row[2] is not None else 4
            
            print(f"SQL Query results - Approval Rate: {approval_rate}%, Avg Cycles: {avg_review_cycles}, Max Cycles: {max_review_cycles}")
        
        # Return the data in the format expected by the frontend
        return Response({
            'approvalRate': approval_rate,
            'avgReviewCycles': avg_review_cycles,
            'maxReviewCycles': max_review_cycles
        })
    
    except Exception as e:
        import traceback
        print(f"ERROR in risk_approval_rate_cycle: {str(e)}")
        print(traceback.format_exc())
        
        # Return fallback data in case of error
        return Response({
            'approvalRate': 81,
            'avgReviewCycles': 3.2,
            'maxReviewCycles': 4
        }, status=200)  # Return 200 OK even for fallback data

@api_view(['GET'])
def risk_register_update_frequency(request):
    """Return data for frequency of risk register updates"""
    print("==== RISK REGISTER UPDATE FREQUENCY ENDPOINT CALLED ====")
    
    try:
        # Calculate average days between risk updates using the provided SQL logic
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT
                    ROUND(AVG(DATEDIFF(next_date, CreatedAt))) AS avg_days_between_inserts
                FROM (
                    SELECT
                        CreatedAt,
                        LEAD(CreatedAt) OVER (ORDER BY CreatedAt) AS next_date
                    FROM risk
                    WHERE CreatedAt IS NOT NULL
                ) t
                WHERE next_date IS NOT NULL;
            """)
            row = cursor.fetchone()
            
        # Get the average days between inserts and convert Decimal to int
        avg_update_frequency = int(row[0]) if row and row[0] is not None else 10  # Default to 10 days if no data
        print(f"Average days between risk register updates: {avg_update_frequency}")
        
        # Generate monthly update counts
        months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        monthly_updates = []
        
        # Current date for reference
        today = timezone.now().date()
        
        # Get data for last 6 months
        for i in range(5, -1, -1):
            month_end = today.replace(day=1) - timedelta(days=1) if i == 0 else (
                today.replace(day=1) - timedelta(days=1) - relativedelta(months=i-1)
            )
            month_start = month_end.replace(day=1)
            
            # Count risks created in this month
            month_count = Risk.objects.filter(
                CreatedAt__gte=month_start,
                CreatedAt__lte=month_end
            ).count()
            
            monthly_updates.append(month_count)
            print(f"Month: {months[5-i]}, Updates: {month_count}")
        
        # Prepare response data - converting any Decimal values to int/float
        response_data = {
            'avgUpdateFrequency': avg_update_frequency,  # Already converted to int above
            'months': months,
            'monthlyUpdates': monthly_updates,  # These are already integers from count()
            'dailyUpdates': [random.randint(0, 3) for _ in range(30)]
        }
        
        # Skip JSON debugging to avoid serialization issues
        print(f"Returning risk register update frequency data")
        return JsonResponse(response_data, safe=False)
    
    except Exception as e:
        import traceback
        print(f"ERROR in risk_register_update_frequency: {str(e)}")
        print(traceback.format_exc())
        
        # Return fallback data
        return JsonResponse({
            'error': str(e),
            'avgUpdateFrequency': 10,  # The value from your SQL screenshot
            'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'monthlyUpdates': [28, 32, 35, 30, 33, 29],
            'dailyUpdates': [random.randint(0, 3) for _ in range(30)]
        }, status=200)  # Return 200 OK even for fallback data

@api_view(['GET'])
def risk_recurrence_probability(request):
    """Return data for probability of risk recurrence"""
    
    # In a real implementation, this would query your database for risk recurrence probability data
    # For demonstration, we'll generate realistic sample data
    
    # Average recurrence probability
    avg_probability = random.randint(32, 48)
    
    # Distribution of risks by recurrence probability ranges
    probability_ranges = [
        {'range': '0-20%', 'count': random.randint(15, 25), 'label': 'Very Low'},
        {'range': '21-40%', 'count': random.randint(25, 35), 'label': 'Low'},
        {'range': '41-60%', 'count': random.randint(20, 30), 'label': 'Medium'},
        {'range': '61-80%', 'count': random.randint(10, 20), 'label': 'High'},
        {'range': '81-100%', 'count': random.randint(5, 15), 'label': 'Very High'}
    ]
    
    # Calculate total for percentages
    total_risks = sum(item['count'] for item in probability_ranges)
    for item in probability_ranges:
        item['percentage'] = round((item['count'] / total_risks) * 100, 1)
    
    # Top risks with high recurrence probability
    high_recurrence_risks = [
        {'id': 1, 'title': 'Service Outage', 'probability': random.randint(75, 95), 'category': 'Operational'},
        {'id': 2, 'title': 'Data Quality Issues', 'probability': random.randint(70, 90), 'category': 'Technology'},
        {'id': 3, 'title': 'Staff Turnover', 'probability': random.randint(65, 85), 'category': 'HR'},
        {'id': 4, 'title': 'Minor Security Breaches', 'probability': random.randint(60, 80), 'category': 'Security'},
        {'id': 5, 'title': 'Vendor Delivery Delays', 'probability': random.randint(60, 75), 'category': 'Supply Chain'}
    ]
    
    # Trend over time (after mitigation)
    trend_data = []
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    
    # Generate trend with slight reduction over time
    base = random.randint(45, 55)
    for i, month in enumerate(months):
        reduction = i * random.uniform(0.8, 2.0)  # Increasing reduction over time
        trend_data.append({
            'month': month,
            'probability': round(max(25, base - reduction), 1)
        })
    
    # Calculate percentage change from previous period
    current = trend_data[-1]['probability']
    previous = trend_data[-2]['probability']
    percentage_change = round(((current - previous) / previous) * 100, 1)
    
    return Response({
        'averageProbability': avg_probability,
        'probabilityRanges': probability_ranges,
        'highRecurrenceRisks': high_recurrence_risks,
        'trendData': trend_data,
        'months': months,
        'percentageChange': percentage_change,
        'totalRisks': total_risks
    })

@api_view(['GET'])
def risk_tolerance_thresholds(request):
    """Return data for organizational risk tolerance thresholds"""
    
    # In a real implementation, this would query your database for risk tolerance threshold settings
    # For demonstration, we'll generate realistic sample data
    
    # Overall tolerance status
    overall_status = random.choice(['Within Limits', 'Near Limits', 'Exceeding Limits'])
    
    # Tolerance thresholds by risk category
    tolerance_thresholds = {
        'Security': {
            'max_exposure': 80,
            'current_exposure': random.randint(65, 95),
            'unit': 'score'
        },
        'Compliance': {
            'max_exposure': 75,
            'current_exposure': random.randint(60, 85),
            'unit': 'score'
        },
        'Operational': {
            'max_exposure': 70,
            'current_exposure': random.randint(60, 80),
            'unit': 'score'
        },
        'Financial': {
            'max_exposure': 5000000,
            'current_exposure': random.randint(3000000, 6000000),
            'unit': 'currency'
        },
        'Strategic': {
            'max_exposure': 85,
            'current_exposure': random.randint(70, 95),
            'unit': 'score'
        }
    }
    
    # Calculate percentage of threshold for each category
    for category, data in tolerance_thresholds.items():
        data['percentage'] = round((data['current_exposure'] / data['max_exposure']) * 100, 1)
        data['status'] = 'Normal' if data['percentage'] <= 85 else 'Warning' if data['percentage'] <= 100 else 'Exceeded'
    
    # Alerts for thresholds exceeded
    alerts = []
    for category, data in tolerance_thresholds.items():
        if data['percentage'] > 100:
            alerts.append({
                'category': category,
                'message': f"{category} risks exceeding defined tolerance threshold by {data['percentage'] - 100:.1f}%",
                'date': (datetime.now() - timedelta(days=random.randint(0, 5))).strftime('%Y-%m-%d')
            })
    
    # Historical threshold data (for trend analysis)
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    historical_data = {}
    
    for category in tolerance_thresholds.keys():
        category_data = []
        base = random.randint(70, 90)
        
        for i, month in enumerate(months):
            # Generate trend with some fluctuation
            variation = random.randint(-8, 10)
            percentage = max(60, min(120, base + variation))
            category_data.append({
                'month': month,
                'percentage': percentage
            })
        
        historical_data[category] = category_data
    
    return Response({
        'overallStatus': overall_status,
        'toleranceThresholds': tolerance_thresholds,
        'alerts': alerts,
        'historicalData': historical_data,
        'months': months
    })

@api_view(['GET'])
def risk_appetite(request):
    """Return risk appetite data for the organization based on risk instances"""
    try:
        print("==== RISK APPETITE ENDPOINT CALLED ====")
        
        # Use raw SQL query similar to what the user ran in MySQL Workbench
        from django.db import connection
        
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT AVG(CAST(Appetite AS FLOAT)) AS avg_appetite
                FROM risk_instance
                WHERE Appetite IS NOT NULL AND Appetite <> ''
            """)
            row = cursor.fetchone()
            
            avg_appetite = row[0] if row and row[0] is not None else None
            print(f"Raw SQL average appetite: {avg_appetite}")
            
            if avg_appetite is not None:
                # Round to 1 decimal place
                avg_appetite = round(float(avg_appetite), 1)
                
                # Determine the label based on the value
                if avg_appetite < 4:
                    label = "Risk Averse"
                elif avg_appetite < 7:
                    label = "Balanced risk approach"
                else:
                    label = "Risk Seeking"
            else:
                avg_appetite = 6  # Default fallback value
                label = "Balanced risk approach"
        
        # Add additional data required by the frontend
        data = {
            'currentLevel': avg_appetite,
            'description': label,
            'historicalLevels': [4, 5, 5, 6, 6, 6],  # Sample historical data
            'dates': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'levelDescriptions': {
                'low': 'Risk Averse (1-3)',
                'medium': 'Balanced (4-7)',
                'high': 'Risk Seeking (8-10)'
            }
        }
        
        print(f"Returning risk appetite data: {data}")
        return Response(data)
    except Exception as e:
        print(f"ERROR in risk_appetite: {str(e)}")
        import traceback
        print(traceback.format_exc())
        
        # Return fallback data in case of error
        return Response({
            'currentLevel': 6,
            'description': 'Balanced risk approach',
            'historicalLevels': [4, 5, 5, 6, 6, 6],
            'dates': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'levelDescriptions': {
                'low': 'Risk Averse (1-3)',
                'medium': 'Balanced (4-7)',
                'high': 'Risk Seeking (8-10)'
            }
        }, status=200)  # Still return 200 for fallback data

@api_view(['GET'])
def active_risks_kpi(request):
    """
    Get the active risks KPI data from the database
    """
    print("==== ACTIVE RISKS KPI ENDPOINT CALLED ====")
    print(f"Request method: {request.method}")
    print(f"Request headers: {request.headers}")
    
    try:
        # Get active risks count (RiskStatus = 'Assigned')
        active_risks_query = RiskInstance.objects.filter(RiskStatus='Assigned')
        active_risks_count = active_risks_query.count()
        
        print(f"Found {active_risks_count} active risks with status 'Assigned'")
        
        # Debug: Print first 5 active risks
        for risk in active_risks_query[:5]:
            print(f"Sample active risk: ID={risk.RiskInstanceId}, Status={risk.RiskStatus}, Date={risk.Date}")
        
        # Get trend data (past 6 months)
        months_count = 6
        current_month = timezone.now().month
        current_year = timezone.now().year
        
        months = []
        trend_data = []
        
        # Generate last N months dynamically and get real data for each month
        for i in range(months_count - 1, -1, -1):
            month_num = ((current_month - i - 1) % 12) + 1
            year = current_year if month_num <= current_month else current_year - 1
            month_name = datetime(year, month_num, 1).strftime('%b')
            months.append(month_name)
            
            # Start and end date for the month
            if month_num == 12:
                next_month = 1
                next_year = year + 1
            else:
                next_month = month_num + 1
                next_year = year
                
            start_date = datetime(year, month_num, 1).date()
            end_date = datetime(next_year, next_month, 1).date() - timedelta(days=1)
            
            # Query for active risks in this month
            month_count = RiskInstance.objects.filter(
                RiskStatus='Assigned',
                Date__gte=start_date,
                Date__lte=end_date
            ).count()
            
            print(f"Month: {month_name}, Date range: {start_date} to {end_date}, Active risks: {month_count}")
            trend_data.append(month_count)
        
        # Current value is the most recent (last) in the trend
        current_value = active_risks_count
        
        # Calculate percentage change from previous month
        if len(trend_data) >= 2 and trend_data[-2] > 0:
            percentage_change = round(((trend_data[-1] - trend_data[-2]) / trend_data[-2]) * 100, 1)
        else:
            percentage_change = 0
        
        print(f"Trend data: {trend_data}")
        print(f"Percentage change: {percentage_change}%")
        
        # Include min/max for charting
        min_value = min(trend_data) if trend_data else 0
        max_value = max(trend_data) if trend_data else 0
        
        response_data = {
            'current': current_value,
            'months': months,
            'trendData': trend_data,
            'percentageChange': percentage_change,
            'minValue': min_value,
            'maxValue': max_value,
            'range': max_value - min_value if trend_data else 0
        }
        
        print(f"Returning KPI data: {json.dumps(response_data)}")
        return JsonResponse(response_data)
    
    except Exception as e:
        print(f"ERROR in active_risks_kpi: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return JsonResponse({
            'error': str(e),
            'current': 0,
            'months': [],
            'trendData': [],
            'percentageChange': 0,
            'minValue': 0,
            'maxValue': 0,
            'range': 0
        }, status=500)

@api_view(['GET'])
def mitigation_completion_rate(request):
    """
    Calculates risk mitigation completion rate and average time to completion
    """
    try:
        # Get the date range (default to last 90 days if not specified)
        today = datetime.now().date()
        start_date = request.query_params.get('start_date', (today - timedelta(days=90)).isoformat())
        end_date = request.query_params.get('end_date', today.isoformat())
        
        # Debug
        print(f"Calculating mitigation completion rate from {start_date} to {end_date}")
        
        # 1. Get total risks in the period
        total_risks = RiskInstance.objects.filter(
            Date__gte=start_date,
            Date__lte=end_date
        ).count()
        
        # 2. Get completed mitigations in the period
        completed_risks = RiskInstance.objects.filter(
            MitigationStatus='Completed',
            MitigationCompletedDate__gte=start_date,
            MitigationCompletedDate__lte=end_date
        ).count()
        
        # 3. Calculate completion rate
        completion_rate = 0
        if total_risks > 0:
            completion_rate = round((completed_risks / total_risks) * 100, 1)
        
        # 4. Calculate average days to mitigation
        avg_days_query = RiskInstance.objects.filter(
            MitigationStatus='Completed',
            Date__isnull=False,
            MitigationCompletedDate__isnull=False,
            MitigationCompletedDate__gte=start_date,
            MitigationCompletedDate__lte=end_date
        ).annotate(
            days_to_mitigate=ExpressionWrapper(
                F('MitigationCompletedDate') - F('Date'), 
                output_field=DurationField()
            )
        ).aggregate(
            avg_days=Avg(Cast('days_to_mitigate', output_field=FloatField()) / (24*3600*1000000))
        )
        
        avg_days = 0
        if avg_days_query['avg_days'] is not None:
            avg_days = round(avg_days_query['avg_days'], 1)
        
        # 5. Define SLA threshold (configurable)
        sla_days = 21  # Default SLA of 21 days
        
        # Debug output
        print(f"Total risks: {total_risks}")
        print(f"Completed mitigations: {completed_risks}")
        print(f"Completion rate: {completion_rate}%")
        print(f"Average days to mitigation: {avg_days}")
        
        # Return the data
        return Response({
            'avgDays': avg_days,
            'slaDays': sla_days,
            'completionRate': completion_rate,
            'totalRisks': total_risks,
            'completedRisks': completed_risks,
            'trendData': [18, 16, 14, 15, 13, 14],  # Sample trend data - to be replaced with real data
            'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']  # Sample months - to be replaced with real data
        })
        
    except Exception as e:
        print(f"Error in mitigation_completion_rate: {str(e)}")
        return Response({
            'avgDays': 14,
            'slaDays': 21,
            'completionRate': 76,
            'totalRisks': 100,
            'completedRisks': 76,
            'trendData': [18, 16, 14, 15, 13, 14],
            'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
def avg_remediation_time(request):
    """
    Get average time to remediate critical risks
    """
    print("==== AVG REMEDIATION TIME ENDPOINT CALLED ====")
    
    try:
        # Optional filter for risk priority
        priority = request.GET.get('priority', 'Critical')
        
        # Calculate average days to remediate for critical risks
        queryset = RiskInstance.objects.filter(
            RiskPriority__iexact=priority,
            MitigationStatus='Completed',
            Date__isnull=False,
            MitigationCompletedDate__isnull=False
        ).annotate(
            days_to_remediate=ExpressionWrapper(
                F('MitigationCompletedDate') - F('Date'), 
                output_field=DurationField()
            )
        )
        
        # Calculate overall average
        avg_days_query = queryset.aggregate(
            avg_days=Avg(Cast('days_to_remediate', output_field=FloatField()) / (24*3600*1000000))
        )
        
        avg_days = round(float(avg_days_query['avg_days'] or 0))
        
        # Define SLA threshold (configurable)
        sla_days = 30  # Default SLA of 30 days for critical risks
        
        # Generate monthly trend data (past 6 months)
        months = []
        trend_data = []
        
        # Current date for reference
        today = timezone.now().date()
        
        # Loop through the last 6 months
        for i in range(5, -1, -1):
            # Calculate month start and end dates
            month_end = today.replace(day=1) - timedelta(days=1) if i == 0 else (
                today.replace(day=1) - timedelta(days=1) - relativedelta(months=i-1)
            )
            month_start = month_end.replace(day=1)
            
            # Get month name for display
            month_name = month_start.strftime('%b')
            months.append(month_name)
            
            # Query for critical risks remediated in this month
            month_avg_query = RiskInstance.objects.filter(
                RiskPriority__iexact=priority,
                MitigationStatus='Completed',
                MitigationCompletedDate__gte=month_start,
                MitigationCompletedDate__lte=month_end,
                Date__isnull=False
            ).annotate(
                days_to_remediate=ExpressionWrapper(
                    F('MitigationCompletedDate') - F('Date'), 
                    output_field=DurationField()
                )
            ).aggregate(
                avg_days=Avg(Cast('days_to_remediate', output_field=FloatField()) / (24*3600*1000000))
            )
            
            month_avg = round(float(month_avg_query['avg_days'] or 0))
            trend_data.append(month_avg)
            print(f"Month: {month_name}, Avg Days: {month_avg}")
        
        # Calculate percentage change
        if len(trend_data) >= 2 and trend_data[-2] > 0:
            percentage_change = round(((trend_data[-1] - trend_data[-2]) / trend_data[-2]) * 100, 1)
        else:
            percentage_change = 0
        
        # Current value is the most recent month's value
        current_value = trend_data[-1] if trend_data else avg_days
        
        # Get overdue critical risks (exceeded SLA)
        overdue_risks = RiskInstance.objects.filter(
            RiskPriority__iexact=priority,
            MitigationStatus__in=['Work in Progress', 'Not Started'],
            Date__lt=today - timedelta(days=sla_days)
        ).count()
        
        # Get total active critical risks
        total_active = RiskInstance.objects.filter(
            RiskPriority__iexact=priority,
            MitigationStatus__in=['Work in Progress', 'Not Started']
        ).count()
        
        # Overdue percentage
        overdue_percentage = round((overdue_risks / total_active * 100) if total_active > 0 else 0)
        
        # Find min and max values for chart scaling
        min_value = min(trend_data) if trend_data else 0
        max_value = max(trend_data) if trend_data else 0
        
        # Ensure SLA is included in the range calculation
        max_value = max(max_value, sla_days)
        
        response_data = {
            'current': current_value,
            'months': months,
            'trendData': trend_data,
            'percentageChange': percentage_change,
            'slaDays': sla_days,
            'overdueCount': overdue_risks,
            'overduePercentage': overdue_percentage,
            'totalActive': total_active,
            'minValue': min_value,
            'maxValue': max_value
        }
        
        print(f"Returning avg remediation time data: {json.dumps(response_data)}")
        return JsonResponse(response_data)
    
    except Exception as e:
        print(f"ERROR in avg_remediation_time: {str(e)}")
        import traceback
        print(traceback.format_exc())
        return JsonResponse({
            'error': str(e),
            'current': 35,
            'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'trendData': [38, 36, 35, 37, 34, 35],
            'percentageChange': 2.5,
            'slaDays': 30,
            'overdueCount': 12,
            'overduePercentage': 15,
            'totalActive': 80,
            'minValue': 34,
            'maxValue': 38
        }, status=500)

@api_view(['GET'])
def recurrence_rate(request):
    """
    Calculate and return the rate of risk recurrence 
    (how often risks reoccur after being closed)
    """
    print("==== RECURRENCE RATE ENDPOINT CALLED ====")
    
    try:
        # Get optional filters
        time_range = request.GET.get('timeRange', 'all')
        category = request.GET.get('category', 'all')
        
        # Base queryset
        queryset = RiskInstance.objects.filter(
            RiskStatus__isnull=False,
            RecurrenceCount__isnull=False
        )
        
        # Apply time filter if specified
        if time_range != 'all':
            today = timezone.now().date()
            start_date = None
            if time_range == '7days':
                start_date = today - timedelta(days=7)
            elif time_range == '30days':
                start_date = today - timedelta(days=30)
            elif time_range == '90days':
                start_date = today - timedelta(days=90)
            elif time_range == '1year':
                start_date = today - timedelta(days=365)
            
            if start_date:
                queryset = queryset.filter(Date__gte=start_date)
                print(f"Applied time filter: {time_range}, records: {queryset.count()}")
        
        # Apply category filter
        if category and category.lower() != 'all':
            category_map = {
                'operational': 'Operational',
                'financial': 'Financial',
                'strategic': 'Strategic', 
                'compliance': 'Compliance',
                'it-security': 'IT Security'
            }
            db_category = category_map.get(category.lower(), category)
            queryset = queryset.filter(Category__iexact=db_category)
            print(f"Applied category filter: {db_category}, records: {queryset.count()}")
        
        # Calculate basic stats
        total_risks = queryset.count()
        recurring_risks = queryset.filter(RecurrenceCount__gt=1).count()
        one_time_risks = total_risks - recurring_risks
        
        recurring_percentage = round((recurring_risks / total_risks) * 100, 1) if total_risks > 0 else 0
        one_time_percentage = 100 - recurring_percentage
        
        print(f"Total risks: {total_risks}")
        print(f"Recurring risks: {recurring_risks} ({recurring_percentage}%)")
        print(f"One-time risks: {one_time_risks} ({one_time_percentage}%)")
        
        # Prepare trend data for last 6 months
        months = []
        trend_data = []
        
        today = timezone.now().date()
        # Starting month: first day of current month minus 5 months
        month_cursor = today.replace(day=1) - relativedelta(months=5)
        
        for _ in range(6):
            month_start = month_cursor
            month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
            month_name = month_start.strftime('%b')
            months.append(month_name)
            
            # Filter risks for month
            month_qs = queryset.filter(Date__gte=month_start, Date__lte=month_end)
            month_total = month_qs.count()
            month_recurring = month_qs.filter(RecurrenceCount__gt=1).count()
            month_rate = round((month_recurring / month_total) * 100, 1) if month_total > 0 else 0
            trend_data.append(month_rate)
            
            print(f"Month: {month_name}, Total: {month_total}, Recurring: {month_recurring}, Rate: {month_rate}%")
            
            month_cursor += relativedelta(months=1)
        
        # Calculate percentage change between last two months
        if len(trend_data) >= 2 and trend_data[-2] > 0:
            percentage_change = round(((trend_data[-1] - trend_data[-2]) / trend_data[-2]) * 100, 1)
        else:
            percentage_change = 0
        
        current_value = trend_data[-1] if trend_data else recurring_percentage
        
        # Category breakdown
        category_breakdown = {}
        for cat in queryset.values_list('Category', flat=True).distinct():
            if not cat:
                continue
            cat_qs = queryset.filter(Category=cat)
            cat_total = cat_qs.count()
            cat_recurring = cat_qs.filter(RecurrenceCount__gt=1).count()
            cat_rate = round((cat_recurring / cat_total) * 100, 1) if cat_total > 0 else 0
            category_breakdown[cat] = cat_rate
        
        # Top recurring risks
        top_recurring_risks = []
        top_risks = queryset.filter(RecurrenceCount__gt=1).order_by('-RecurrenceCount')[:5]
        
        for risk in top_risks:
            title = (risk.RiskDescription[:47] + "...") if risk.RiskDescription and len(risk.RiskDescription) > 50 else (risk.RiskDescription or f"Risk {risk.RiskInstanceId}")
            top_recurring_risks.append({
                'id': risk.RiskInstanceId,
                'title': title,
                'category': risk.Category or "Unknown",
                'count': risk.RecurrenceCount,
                'owner': risk.RiskOwner
            })
        
        # Prepare response
        response_data = {
            'recurrenceRate': recurring_percentage,
            'oneTimeRate': one_time_percentage,
            'totalRisks': total_risks,
            'recurringRisks': recurring_risks,
            'oneTimeRisks': one_time_risks,
            'months': months,
            'trendData': trend_data,
            'percentageChange': percentage_change,
            'breakdown': category_breakdown,
            'topRecurringRisks': top_recurring_risks
        }
        
        print(f"Returning recurrence rate data: {json.dumps(response_data)}")
        return JsonResponse(response_data)
    
    except Exception as e:
        import traceback
        print(f"ERROR in recurrence_rate: {str(e)}")
        print(traceback.format_exc())
        # Return default or error fallback data
        return JsonResponse({
            'error': str(e),
            'recurrenceRate': 6.5,
            'oneTimeRate': 93.5,
            'totalRisks': 200,
            'recurringRisks': 13,
            'oneTimeRisks': 187,
            'months': ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun'],
            'trendData': [5.8, 6.2, 6.7, 6.3, 6.8, 6.5],
            'percentageChange': -4.4,
            'breakdown': {
                'Security': 8.4,
                'Compliance': 5.2,
                'Operational': 7.3,
                'Financial': 4.8
            },
            'topRecurringRisks': [
                {'id': 1, 'title': 'System Outage', 'category': 'Operational', 'count': 4, 'owner': 'IT Department'},
                {'id': 2, 'title': 'Data Quality Issues', 'category': 'Technology', 'count': 3, 'owner': 'Data Team'},
                {'id': 3, 'title': 'Vendor Delivery Delays', 'category': 'Supply Chain', 'count': 3, 'owner': 'Procurement'},
                {'id': 4, 'title': 'Staff Turnover', 'category': 'HR', 'count': 2, 'owner': 'HR Department'},
                {'id': 5, 'title': 'Security Breach', 'category': 'Security', 'count': 2, 'owner': 'Security Team'}
            ]
        }, status=500)

@api_view(['GET'])
def avg_incident_response_time(request):
    """
    Calculate the average time between incident detection and response start
    based on the incident table data
    """
    print("==== AVG INCIDENT RESPONSE TIME ENDPOINT CALLED ====")
    
    try:
        # Get optional filters
        time_range = request.GET.get('timeRange', 'all')
        category = request.GET.get('category', 'all')
        
        # Use direct SQL query to calculate average response time
        with connection.cursor() as cursor:
            query = """
                SELECT AVG(TIMESTAMPDIFF(SECOND, IdentifiedAt, CreatedAt)) / 3600 AS avg_response_time_hours
                FROM incidents
                WHERE IdentifiedAt IS NOT NULL 
                AND CreatedAt IS NOT NULL
            """
            
            # Add time filter if specified
            if time_range != 'all':
                today = timezone.now().date()
                start_date = None
                if time_range == '7days':
                    start_date = today - timedelta(days=7)
                elif time_range == '30days':
                    start_date = today - timedelta(days=30)
                elif time_range == '90days':
                    start_date = today - timedelta(days=90)
                elif time_range == '1year':
                    start_date = today - timedelta(days=365)
                
                if start_date:
                    query += f" AND Date >= '{start_date.isoformat()}'"
            
            # Add category filter if specified
            if category and category.lower() != 'all':
                category_map = {
                    'operational': 'Operational',
                    'financial': 'Financial',
                    'strategic': 'Strategic', 
                    'compliance': 'Compliance',
                    'it-security': 'IT Security'
                }
                db_category = category_map.get(category.lower(), category)
                query += f" AND RiskCategory = '{db_category}'"
            
            # Execute the query
            cursor.execute(query)
            result = cursor.fetchone()
            
            # Get the average hours (handle NULL/None case)
            avg_hours = result[0] if result and result[0] is not None else 0
            
            # If average is negative (CreatedAt before IdentifiedAt), we use absolute value
            # This can happen if dates are entered incorrectly in the system
            avg_hours = abs(float(avg_hours))
            
            # Round to 1 decimal place
            avg_hours = round(avg_hours, 1)
            
            print(f"SQL Query result: {result}")
            print(f"Average response time: {avg_hours} hours")
        
        # Calculate the number of delayed incidents (exceeding SLA)
        delayed_incidents = 0
        total_incidents = 0
        
        # Define SLA thresholds
        target_hours = 4  # Target response time (4 hours)
        sla_hours = 8     # SLA threshold (8 hours)
        
        # Query for delayed incidents
        with connection.cursor() as cursor:
            cursor.execute("""
                SELECT COUNT(*) FROM incidents
                WHERE IdentifiedAt IS NOT NULL 
                AND CreatedAt IS NOT NULL
                AND ABS(TIMESTAMPDIFF(SECOND, IdentifiedAt, CreatedAt)) / 3600 > %s
            """, [sla_hours])
            
            delayed_incidents = cursor.fetchone()[0]
            
            # Get total incidents count
            cursor.execute("""
                SELECT COUNT(*) FROM incidents
                WHERE IdentifiedAt IS NOT NULL 
                AND CreatedAt IS NOT NULL
            """)
            
            total_incidents = cursor.fetchone()[0]
        
        # Calculate percentage of delayed incidents
        delayed_percentage = 0
        if total_incidents > 0:
            delayed_percentage = round((delayed_incidents / total_incidents) * 100, 1)
        
        print(f"Total incidents: {total_incidents}")
        print(f"Delayed incidents: {delayed_incidents} ({delayed_percentage}%)")
        
        # Generate monthly trend data (past 6 months)
        months = []
        trend_data = []
        
        # Current date for reference
        today = timezone.now().date()
        
        # Starting month: first day of current month minus 5 months
        month_cursor = today.replace(day=1) - relativedelta(months=5)
        
        for _ in range(6):
            month_start = month_cursor
            month_end = (month_start + relativedelta(months=1)) - timedelta(days=1)
            month_name = month_start.strftime('%b')
            months.append(month_name)
            
            # Query for average response time in this month
            with connection.cursor() as cursor:
                cursor.execute("""
                    SELECT AVG(ABS(TIMESTAMPDIFF(SECOND, IdentifiedAt, CreatedAt))) / 3600 AS avg_response_time_hours
                    FROM incidents
                    WHERE IdentifiedAt IS NOT NULL 
                    AND CreatedAt IS NOT NULL
                    AND Date BETWEEN %s AND %s
                """, [month_start, month_end])
                
                result = cursor.fetchone()
                month_avg = float(result[0]) if result and result[0] is not None else 0
                month_avg = round(month_avg, 1)
            
            trend_data.append(month_avg)
            print(f"Month: {month_name}, Avg Hours: {month_avg}")
            
            month_cursor += relativedelta(months=1)
        
        # Calculate percentage change
        if len(trend_data) >= 2 and trend_data[-2] > 0:
            percentage_change = round(((trend_data[-1] - trend_data[-2]) / trend_data[-2]) * 100, 1)
        else:
            percentage_change = 0
        
        # Convert all decimal values to float for JSON serialization
        # This prevents the "Object of type Decimal is not JSON serializable" error
        response_data = {
            'current': float(avg_hours),
            'target': float(target_hours),
            'sla': float(sla_hours),
            'months': months,
            'trendData': [float(val) for val in trend_data],
            'percentageChange': float(percentage_change),
            'delayedCount': int(delayed_incidents),
            'delayedPercentage': float(delayed_percentage),
            'totalIncidents': int(total_incidents)
        }
        
        print(f"Returning avg incident response time data: {json.dumps(response_data)}")
        return JsonResponse(response_data)
    
    except Exception as e:
        import traceback
        print(f"ERROR in avg_incident_response_time: {str(e)}")
        print(traceback.format_exc())
        
        # Return fallback data in case of error
        return JsonResponse({
            'error': str(e),
            'current': 457.4,
            'target': 4,
            'sla': 8,
            'months': ['Dec', 'Jan', 'Feb', 'Mar', 'Apr', 'May'],
            'trendData': [400, 410, 405, 420, 430, 457.4],
            'percentageChange': 6.4,
            'delayedCount': 18,
            'delayedPercentage': 95,
            'totalIncidents': 19
        }, status=500)

@api_view(['GET'])
def mitigation_cost(request):
    """
    Calculate and return the cost of mitigation for risks
    """
    print("==== MITIGATION COST ENDPOINT CALLED ====")
    
    try:
        # Get optional filters
        time_range = request.GET.get('timeRange', 'all')
        category = request.GET.get('category', 'all')
        
        # Define time period
        today = timezone.now().date()
        start_date = None
        
        if time_range != 'all':
            if time_range == '30days':
                start_date = today - timedelta(days=30)
            elif time_range == '90days':
                start_date = today - timedelta(days=90)
            elif time_range == '6months':
                start_date = today - timedelta(days=180)
            elif time_range == '1year':
                start_date = today - timedelta(days=365)
            else:
                start_date = today - timedelta(days=30)  # Default to 30 days
        
        # Query for risks with completed mitigations in the period
        queryset = RiskInstance.objects.filter(
            MitigationStatus='Completed'
        )
        
        if start_date:
            queryset = queryset.filter(
                MitigationCompletedDate__gte=start_date,
                MitigationCompletedDate__lte=today
            )
            print(f"Applied time filter: {time_range}, records: {queryset.count()}")
        
        # Apply category filter if specified
        if category and category.lower() != 'all':
            category_map = {
                'operational': 'Operational',
                'financial': 'Financial',
                'strategic': 'Strategic', 
                'compliance': 'Compliance',
                'it-security': 'IT Security'
            }
            db_category = category_map.get(category.lower(), category)
            queryset = queryset.filter(Category__iexact=db_category)
            print(f"Applied category filter: {db_category}, records: {queryset.count()}")
        
        # Get total number of mitigated risks
        total_mitigated = queryset.count()
        print(f"Total mitigated risks: {total_mitigated}")
        
        # Calculate cost based on RiskExposureRating
        # For demo purposes, we'll use a formula: each exposure point = 1000 currency units
        cost_factor = 1000
        
        # Calculate total cost
        total_exposure = queryset.aggregate(
            total=models.Sum('RiskExposureRating')
        )['total'] or 0
        
        total_cost = round(float(total_exposure) * cost_factor / 1000)  # Convert to K
        print(f"Total exposure: {total_exposure}, Total cost: {total_cost}K")
        
        # Calculate average cost per mitigation
        avg_cost = round(total_cost / total_mitigated) if total_mitigated > 0 else 0
        print(f"Average cost per mitigation: {avg_cost}K")
        
        # Generate monthly data for the last 6 months
        monthly_data = []
        months = []
        
        # Generate data for the last 6 months
        for i in range(5, -1, -1):
            month_end = today.replace(day=1) - timedelta(days=1) if i == 0 else (
                today.replace(day=1) - timedelta(days=1) - relativedelta(months=i-1)
            )
            month_start = month_end.replace(day=1)
            
            month_name = month_start.strftime('%b')
            months.append(month_name)
            
            # Get total exposure for risks mitigated in this month
            month_exposure = RiskInstance.objects.filter(
                MitigationStatus='Completed',
                MitigationCompletedDate__gte=month_start,
                MitigationCompletedDate__lte=month_end
            ).aggregate(
                total=models.Sum('RiskExposureRating')
            )['total'] or 0
            
            month_cost = round(float(month_exposure) * cost_factor / 1000)  # Convert to K
            monthly_data.append({
                'month': month_name,
                'cost': month_cost
            })
            
            print(f"Month: {month_name}, Exposure: {month_exposure}, Cost: {month_cost}K")
        
        # Calculate highest cost category
        highest_category = {'category': 'None', 'cost': 0}
        
        for cat in RiskInstance.objects.values_list('Category', flat=True).distinct():
            if not cat:
                continue
                
            cat_exposure = RiskInstance.objects.filter(
                MitigationStatus='Completed',
                Category=cat
            )
            
            if start_date:
                cat_exposure = cat_exposure.filter(
                    MitigationCompletedDate__gte=start_date,
                    MitigationCompletedDate__lte=today
                )
            
            cat_exposure_sum = cat_exposure.aggregate(
                total=models.Sum('RiskExposureRating')
            )['total'] or 0
            
            cat_cost = round(float(cat_exposure_sum) * cost_factor / 1000)
            
            if cat_cost > highest_category['cost']:
                highest_category = {'category': cat, 'cost': cat_cost}
        
        print(f"Highest cost category: {highest_category['category']} at {highest_category['cost']}K")
        
        # Calculate percentage change from previous period
        prev_period_end = None
        prev_period_start = None
        
        if time_range == '30days':
            prev_period_end = today - timedelta(days=30)
            prev_period_start = prev_period_end - timedelta(days=30)
        elif time_range == '90days':
            prev_period_end = today - timedelta(days=90)
            prev_period_start = prev_period_end - timedelta(days=90)
        elif time_range == '6months':
            prev_period_end = today - timedelta(days=180)
            prev_period_start = prev_period_end - timedelta(days=180)
        elif time_range == '1year':
            prev_period_end = today - timedelta(days=365)
            prev_period_start = prev_period_end - timedelta(days=365)
        else:
            prev_period_end = today - timedelta(days=30)
            prev_period_start = prev_period_end - timedelta(days=30)
        
        prev_exposure = RiskInstance.objects.filter(
            MitigationStatus='Completed',
            MitigationCompletedDate__gte=prev_period_start,
            MitigationCompletedDate__lte=prev_period_end
        )
        
        if category and category.lower() != 'all':
            prev_exposure = prev_exposure.filter(Category__iexact=db_category)
            
        prev_exposure_sum = prev_exposure.aggregate(
            total=models.Sum('RiskExposureRating')
        )['total'] or 0
        
        prev_cost = round(float(prev_exposure_sum) * cost_factor / 1000)
        
        # Calculate percentage change
        percentage_change = 0
        if prev_cost > 0:
            percentage_change = round(((total_cost - prev_cost) / prev_cost) * 100, 1)
        
        print(f"Previous period cost: {prev_cost}K, Percentage change: {percentage_change}%")
        
        # Get highest monthly cost for display
        highest_cost = max([item['cost'] for item in monthly_data]) if monthly_data else 0
        
        # Return response
        response_data = {
            'totalCost': total_cost,
            'avgCost': avg_cost,
            'highestCost': highest_cost,
            'highestCategory': highest_category['category'],
            'percentageChange': percentage_change,
            'monthlyData': monthly_data,
            'totalMitigated': total_mitigated
        }
        
        print(f"Returning mitigation cost data: {json.dumps(response_data)}")
        return Response(response_data)
    
    except Exception as e:
        import traceback
        print(f"ERROR in mitigation_cost: {str(e)}")
        print(traceback.format_exc())
        
        # Return fallback data in case of error
        return Response({
            'error': str(e),
            'totalCost': 184,
            'avgCost': 31,
            'highestCost': 42,
            'highestCategory': 'Security',
            'percentageChange': 5.7,
            'monthlyData': [
                {'month': 'Jan', 'cost': 35},
                {'month': 'Feb', 'cost': 28},
                {'month': 'Mar', 'cost': 42},
                {'month': 'Apr', 'cost': 31},
                {'month': 'May', 'cost': 25},
                {'month': 'Jun', 'cost': 23}
            ],
            'totalMitigated': 6
        }, status=500)

@api_view(['GET'])
def risk_assessment_consensus(request):
    """Return data for risk assessment consensus"""
    
    # In a real implementation, this would query your database for risk assessment consensus data
    # For demonstration, we'll generate realistic sample data
    
    # Overall consensus percentage
    consensus_percentage = random.randint(65, 85)
    
    # Consensus by risk category
    category_consensus = {
        'Security': random.randint(70, 90),
        'Operational': random.randint(60, 80),
        'Compliance': random.randint(75, 95),
        'Financial': random.randint(65, 85),
        'Strategic': random.randint(55, 75)
    }
    
    # Consensus breakdown
    total_assessments = random.randint(80, 120)
    consensus_count = int(total_assessments * consensus_percentage / 100)
    no_consensus_count = total_assessments - consensus_count
    
    # Recent assessments with no consensus (for investigation)
    low_consensus_risks = [
        {'id': 1, 'title': 'Cloud Migration Security', 'category': 'Security', 'reviewers': 4, 'agreement': '2/4'},
        {'id': 2, 'title': 'Third-party Vendor Assessment', 'category': 'Operational', 'reviewers': 3, 'agreement': '1/3'},
        {'id': 3, 'title': 'New Regulatory Requirements', 'category': 'Compliance', 'reviewers': 5, 'agreement': '3/5'},
        {'id': 4, 'title': 'Financial Projection Accuracy', 'category': 'Financial', 'reviewers': 3, 'agreement': '1/3'},
        {'id': 5, 'title': 'Market Entry Strategy', 'category': 'Strategic', 'reviewers': 4, 'agreement': '2/4'}
    ]
    
    # Monthly trend data
    months = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun']
    monthly_consensus = [random.randint(60, 90) for _ in months]
    
    return Response({
        'consensusPercentage': consensus_percentage,
        'totalAssessments': total_assessments,
        'consensusCount': consensus_count,
        'noConsensusCount': no_consensus_count,
        'categoryConsensus': category_consensus,
        'lowConsensusRisks': low_consensus_risks,
        'months': months,
        'monthlyConsensus': monthly_consensus
    })

