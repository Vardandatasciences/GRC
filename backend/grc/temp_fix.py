@api_view(['GET'])
def risk_recurrence_probability(request):
    """Return data for probability of risk recurrence"""
    # Simple fallback data that matches the image
    return JsonResponse({
        "averageProbability": 38,
        "percentageChange": -6.2,
        "probabilityRanges": [
            {"range": "0-20%", "count": 20},
            {"range": "21-40%", "count": 30},
            {"range": "41-60%", "count": 25},
            {"range": "61-80%", "count": 15},
            {"range": "81-100%", "count": 10}
        ],
        "highRecurrenceRisks": [
            {"id": 1, "title": "Service Outage", "probability": 85, "category": "Operational"}
        ],
        "totalRisks": 100
    }) 