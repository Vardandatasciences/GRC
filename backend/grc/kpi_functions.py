from django.db import connection
from django.http import JsonResponse
from datetime import datetime, timedelta
from dateutil.relativedelta import relativedelta
import json

def get_audit_completion_kpi(request):
    """
    Calculate and return KPI data for Audits Completed vs. Planned
    
    Query parameters:
    - period: The time period for the KPI (day, week, month, quarter, year)
    - start_date: Optional start date (YYYY-MM-DD)
    - end_date: Optional end date (YYYY-MM-DD)
    """
    period = request.GET.get('period', 'month')
    
    # If start and end dates are provided, use them
    if 'start_date' in request.GET and 'end_date' in request.GET:
        start_date = request.GET.get('start_date')
        end_date = request.GET.get('end_date')
    else:
        # Otherwise calculate based on the period
        end_date = datetime.now().date()
        
        if period == 'day':
            start_date = end_date
        elif period == 'week':
            start_date = end_date - timedelta(days=7)
        elif period == 'month':
            start_date = end_date - relativedelta(months=1)
        elif period == 'quarter':
            start_date = end_date - relativedelta(months=3)
        elif period == 'year':
            start_date = end_date - relativedelta(years=1)
        else:
            # Default to month
            start_date = end_date - relativedelta(months=1)
    
    # Convert string dates to datetime objects if they are strings
    if isinstance(start_date, str):
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
    if isinstance(end_date, str):
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    
    # Format dates for SQL query
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # Build the SQL query
    query = """
    SELECT
        COUNT(*) AS planned_count,
        SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed_count
    FROM
        grc_audit
    WHERE
        created_at BETWEEN %s AND %s
    """
    
    # Execute the query
    with connection.cursor() as cursor:
        cursor.execute(query, [start_date_str, end_date_str])
        row = cursor.fetchone()
    
    # Calculate the KPI values
    planned_count = row[0] if row[0] else 0
    completed_count = row[1] if row[1] else 0
    completion_percentage = round((completed_count / planned_count) * 100, 2) if planned_count > 0 else 0
    
    # Determine the status based on a target threshold (can be customized)
    target_percentage = 85  # 85% completion target
    
    if completion_percentage >= target_percentage:
        status = "Target Achieved"
        status_class = "success"
    elif completion_percentage >= target_percentage * 0.85:
        status = "Near Target"
        status_class = "warning"
    else:
        status = "Below Target"
        status_class = "danger"
    
    # Prepare the response data
    response_data = {
        "period_label": format_period_label(start_date, end_date, period),
        "planned": planned_count,
        "completed": completed_count,
        "completion_percentage": completion_percentage,
        "target": target_percentage,
        "status": status,
        "status_class": status_class
    }
    
    return JsonResponse(response_data)

def get_audit_completion_trend(request):
    """
    Get audit completion trend data over time periods
    
    Query parameters:
    - period: The time period breakdown (day, week, month)
    - time_span: The overall time span (week, month, quarter, year)
    """
    period = request.GET.get('period', 'week')
    time_span = request.GET.get('time_span', 'month')
    
    # Calculate the end date (today) and start date based on time_span
    end_date = datetime.now().date()
    
    if time_span == 'week':
        start_date = end_date - timedelta(days=7)
    elif time_span == 'month':
        start_date = end_date - relativedelta(months=1)
    elif time_span == 'quarter':
        start_date = end_date - relativedelta(months=3)
    elif time_span == 'year':
        start_date = end_date - relativedelta(years=1)
    else:
        # Default to month
        start_date = end_date - relativedelta(months=1)
    
    # Format dates for SQL query
    start_date_str = start_date.strftime('%Y-%m-%d')
    end_date_str = end_date.strftime('%Y-%m-%d')
    
    # Build the appropriate SQL query based on the period
    if period == 'day':
        date_format = '%Y-%m-%d'
        date_trunc = 'DATE(created_at)'
    elif period == 'week':
        date_format = 'Week %V, %Y'
        date_trunc = "CONCAT('Week ', WEEK(created_at), ', ', YEAR(created_at))"
    elif period == 'month':
        date_format = '%b %Y'
        date_trunc = "DATE_FORMAT(created_at, '%Y-%m')"
    else:
        # Default to week
        date_format = 'Week %V, %Y'
        date_trunc = "CONCAT('Week ', WEEK(created_at), ', ', YEAR(created_at))"
    
    query = f"""
    SELECT
        {date_trunc} AS time_period,
        COUNT(*) AS planned_count,
        SUM(CASE WHEN status = 'Completed' THEN 1 ELSE 0 END) AS completed_count
    FROM
        grc_audit
    WHERE
        created_at BETWEEN %s AND %s
    GROUP BY
        time_period
    ORDER BY
        MIN(created_at)
    """
    
    # Execute the query
    with connection.cursor() as cursor:
        cursor.execute(query, [start_date_str, end_date_str])
        rows = cursor.fetchall()
    
    # Prepare the trend data
    trend_data = []
    for row in rows:
        time_period = row[0]
        planned = row[1]
        completed = row[2]
        percentage = round((completed / planned) * 100, 2) if planned > 0 else 0
        
        trend_data.append({
            "time_period": time_period,
            "planned": planned,
            "completed": completed,
            "percentage": percentage
        })
    
    return JsonResponse({"trend_data": trend_data})

def format_period_label(start_date, end_date, period):
    """Format a human-readable label for the time period"""
    if period == 'day':
        return start_date.strftime('%b %d, %Y')
    elif period == 'week':
        return f"Week of {start_date.strftime('%b %d')} - {end_date.strftime('%b %d, %Y')}"
    elif period == 'month':
        if start_date.month == end_date.month and start_date.year == end_date.year:
            return start_date.strftime('%B %Y')
        else:
            return f"{start_date.strftime('%b %Y')} - {end_date.strftime('%b %Y')}"
    elif period == 'quarter':
        start_quarter = (start_date.month - 1) // 3 + 1
        end_quarter = (end_date.month - 1) // 3 + 1
        if start_date.year == end_date.year and start_quarter == end_quarter:
            return f"Q{start_quarter} {start_date.year}"
        else:
            return f"Q{start_quarter} {start_date.year} - Q{end_quarter} {end_date.year}"
    elif period == 'year':
        if start_date.year == end_date.year:
            return str(start_date.year)
        else:
            return f"{start_date.year} - {end_date.year}"
    else:
        return f"{start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}"
