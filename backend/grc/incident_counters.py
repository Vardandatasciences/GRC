from django.http import JsonResponse
from .models import Incident

def get_incident_counts(request):
    """
    Get counts of incidents by status for the dashboard
    """
    print("Received request for incident counts")

    total_incidents = Incident.objects.count()
    print(f"Total incidents count: {total_incidents}")

    pending_incidents = Incident.objects.filter(Status__iexact='Scheduled').count()
    print(f"Pending incidents count (Scheduled): {pending_incidents}")

    accepted_incidents = Incident.objects.filter(Status__iexact='Accepted').count()
    print(f"Accepted incidents count: {accepted_incidents}")
    
    rejected_incidents = Incident.objects.filter(Status__iexact='Rejected').count()
    print(f"Rejected incidents count: {rejected_incidents}")

    resolved_incidents = Incident.objects.filter(Status__iexact='Mitigated').count()
    print(f"Resolved incidents count (Mitigated): {resolved_incidents}")

    data = {
        'total': total_incidents,
        'pending': pending_incidents,
        'accepted': accepted_incidents,
        'rejected': rejected_incidents,
        'resolved': resolved_incidents
    }

    print(f"Returning JSON response data: {data}")
    return JsonResponse(data) 