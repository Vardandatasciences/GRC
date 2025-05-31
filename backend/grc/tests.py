from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from .models import RiskInstance
import json
from datetime import datetime, timedelta

# Create your tests here.

class RecurrenceRateTests(TestCase):
    """Test the recurrence rate API endpoint"""
    
    def setUp(self):
        """Set up test data"""
        # Create sample risk instances with different recurrence counts
        RiskInstance.objects.create(
            RiskDescription="One-time risk",
            Category="Security",
            RecurrenceCount=1,
            RiskStatus="Closed",
            Date=datetime.now().date()
        )
        
        RiskInstance.objects.create(
            RiskDescription="Recurring risk 1",
            Category="Operational",
            RecurrenceCount=3,
            RiskStatus="Closed",
            Date=datetime.now().date()
        )
        
        RiskInstance.objects.create(
            RiskDescription="Recurring risk 2",
            Category="Compliance",
            RecurrenceCount=2,
            RiskStatus="Closed",
            Date=datetime.now().date()
        )
        
        RiskInstance.objects.create(
            RiskDescription="One-time risk 2",
            Category="Financial",
            RecurrenceCount=1,
            RiskStatus="Closed",
            Date=datetime.now().date()
        )
        
        # Create a client for making API requests
        self.client = APIClient()
    
    def test_recurrence_rate_endpoint(self):
        """Test the recurrence rate API endpoint returns correct data"""
        # Make a GET request to the endpoint
        url = reverse('recurrence_rate')
        response = self.client.get(url)
        
        # Check the response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Parse the response data
        response_data = json.loads(response.content)
        
        # Check the core fields are present
        self.assertIn('recurrenceRate', response_data)
        self.assertIn('oneTimeRate', response_data)
        self.assertIn('totalRisks', response_data)
        self.assertIn('recurringRisks', response_data)
        self.assertIn('oneTimeRisks', response_data)
        
        # Verify the calculations are correct
        self.assertEqual(response_data['totalRisks'], 4)
        self.assertEqual(response_data['recurringRisks'], 2)
        self.assertEqual(response_data['oneTimeRisks'], 2)
        
        # Expected recurrence rate: 2/4 * 100 = 50%
        self.assertEqual(response_data['recurrenceRate'], 50.0)
        self.assertEqual(response_data['oneTimeRate'], 50.0)
        
        # Check that trend data is included
        self.assertIn('trendData', response_data)
        self.assertIn('months', response_data)
    
    def test_recurrence_rate_with_category_filter(self):
        """Test the recurrence rate API endpoint with category filter"""
        # Make a GET request with category filter
        url = reverse('recurrence_rate')
        response = self.client.get(url, {'category': 'operational'})
        
        # Check the response status
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Parse the response data
        response_data = json.loads(response.content)
        
        # Verify the filtered calculations are correct
        self.assertEqual(response_data['totalRisks'], 1)
        self.assertEqual(response_data['recurringRisks'], 1)
        self.assertEqual(response_data['oneTimeRisks'], 0)
        
        # Expected recurrence rate: 1/1 * 100 = 100%
        self.assertEqual(response_data['recurrenceRate'], 100.0)
        self.assertEqual(response_data['oneTimeRate'], 0.0)
