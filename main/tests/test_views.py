from django.test import TestCase
from main.models import Location, ClimateReading
from django.db import IntegrityError
from api.location.views import LocationView
from rest_framework.test import APIRequestFactory
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch

class LocationViewsTestCases(TestCase):
    def setUp(self):
        """Set up test data and API request factory"""
        self.factory = APIRequestFactory()
        self.view = LocationView.as_view()
        
        # Create a test location
        self.test_location = Location.objects.create(
            name="Test Location",
            latitude=45.0,
            longitude=45.0,
            description="Test Description"
        )
        
        # Data for creating a new location
        self.new_location_data = {
            "name": "New Test Location",
            "latitude": 50.0,
            "longitude": 50.0,
            "description": "New Test Description"
        }
    
    def test_get_location_success(self):
        """Test successful retrieval of a location"""
        request = self.factory.get('/api/location/', {'name': self.test_location.name})
        response = self.view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.test_location.name)
        self.assertEqual(float(response.data['latitude']), self.test_location.latitude)
        self.assertEqual(float(response.data['longitude']), self.test_location.longitude)
    
    def test_get_location_missing_name(self):
        """Test error when name parameter is missing"""
        request = self.factory.get('/api/location/')
        response = self.view(request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], "Name is required to identify the location.")
    
    def test_get_location_not_found(self):
        """Test error when location doesn't exist"""
        request = self.factory.get('/api/location/', {'name': 'Non-existent Location'})
        
        with self.assertRaises(Location.DoesNotExist):
            self.view(request)
    
    @patch('api.location.views.ClimateDataProvider')
    @patch('api.location.views.process_climate_data')
    @patch('api.location.views.create_climate_readings')
    def test_post_location_success(self, mock_create_readings, mock_process_data, mock_provider_class):
        """Test successful creation of a location with mocked climate data processing"""
        # Setup mocks
        mock_provider = mock_provider_class.return_value
        mock_provider.get_climate_data.return_value = {f"{self.new_location_data['latitude']},{self.new_location_data['longitude']}": []}
        mock_process_data.return_value = []
        
        # Make request
        request = self.factory.post('/api/location/', self.new_location_data, format='json')
        response = self.view(request)
        
        # Verify response and database state
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Location.objects.filter(name=self.new_location_data['name']).exists())
        
        # Verify mocks were called
        mock_provider.get_climate_data.assert_called_once()
        mock_process_data.assert_called_once()
        mock_create_readings.assert_called_once()
    
    def test_post_location_missing_fields(self):
        """Test error when required fields are missing"""
        incomplete_data = {"name": "Incomplete Location"}
        request = self.factory.post('/api/location/', incomplete_data, format='json')
        response = self.view(request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], "Missing required fields.")
    
    def test_post_location_duplicate_name(self):
        """Test error when location with same name already exists"""
        duplicate_data = {
            "name": self.test_location.name,  # Same name as existing location
            "latitude": 60.0,
            "longitude": 60.0,
            "description": "Duplicate Name"
        }
        request = self.factory.post('/api/location/', duplicate_data, format='json')
        response = self.view(request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], "Location with this name or exact latitude and longitude already exists.")
    
    def test_delete_location_success(self):
        """Test successful deletion of a location"""
        request = self.factory.delete(f'/api/location?name={self.test_location.name}')
        response = self.view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Location.objects.filter(name=self.test_location.name).exists())
    
    def test_delete_location_missing_name(self):
        """Test error when name parameter is missing for deletion"""
        request = self.factory.delete('/api/location/')
        response = self.view(request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], "Name is required to identify the location to delete.")
    
    def test_delete_location_not_found(self):
        """Test error when trying to delete non-existent location"""
        request = self.factory.delete(f'/api/location?name="Non-existent Location"')
        response = self.view(request)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['message'], "Location with this name does not exist.")
