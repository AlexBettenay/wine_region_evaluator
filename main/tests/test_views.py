from django.test import TestCase
from main.models import Region, ClimateReading
from django.db import IntegrityError
from api.region.views import RegionView
from rest_framework.test import APIRequestFactory
from django.urls import reverse
from rest_framework import status
from unittest.mock import patch

class RegionViewsTestCases(TestCase):
    def setUp(self):
        """Set up test data and API request factory"""
        self.factory = APIRequestFactory()
        self.view = RegionView.as_view()
        
        # Create a test region
        self.test_region = Region.objects.create(
            name="Test Region",
            latitude=45.0,
            longitude=45.0,
            description="Test Description"
        )
        
        # Data for creating a new region
        self.new_region_data = {
            "name": "New Test Region",
            "latitude": 50.0,
            "longitude": 50.0,
            "description": "New Test Description"
        }
    
    def test_get_region_success(self):
        """Test successful retrieval of a region"""
        request = self.factory.get('/api/region/', {'name': self.test_region.name})
        response = self.view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['name'], self.test_region.name)
        self.assertEqual(float(response.data['latitude']), self.test_region.latitude)
        self.assertEqual(float(response.data['longitude']), self.test_region.longitude)
    
    def test_get_region_missing_name(self):
        """Test error when name parameter is missing"""
        request = self.factory.get('/api/region/')
        response = self.view(request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], "Name is required to identify the Region.")
    
    def test_get_region_not_found(self):
        """Test error when region doesn't exist"""
        request = self.factory.get('/api/region/', {'name': 'Non-existent Region'})
        
        with self.assertRaises(Region.DoesNotExist):
            self.view(request)
    
    @patch('api.region.views.ClimateDataProvider')
    @patch('api.region.views.process_climate_data')
    @patch('api.region.views.create_climate_readings')
    def test_post_region_success(self, mock_create_readings, mock_process_data, mock_provider_class):
        """Test successful creation of a region with mocked climate data processing"""
        # Setup mocks
        mock_provider = mock_provider_class.return_value
        mock_provider.get_climate_data.return_value = {f"{self.new_region_data['latitude']},{self.new_region_data['longitude']}": []}
        mock_process_data.return_value = []
        
        # Make request
        request = self.factory.post('/api/region/', self.new_region_data, format='json')
        response = self.view(request)
        
        # Verify response and database state
        self.assertEqual(response.status_code, 200)
        self.assertTrue(Region.objects.filter(name=self.new_region_data['name']).exists())
        
        # Verify mocks were called
        mock_provider.get_climate_data.assert_called_once()
        mock_process_data.assert_called_once()
        mock_create_readings.assert_called_once()
    
    def test_post_region_missing_fields(self):
        """Test error when required fields are missing"""
        incomplete_data = {"name": "Incomplete Region"}
        request = self.factory.post('/api/region/', incomplete_data, format='json')
        response = self.view(request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], "Missing required fields.")
    
    def test_post_region_duplicate_name(self):
        """Test error when region with same name already exists"""
        duplicate_data = {
            "name": self.test_region.name,  # Same name as existing region
            "latitude": 60.0,
            "longitude": 60.0,
            "description": "Duplicate Name"
        }
        request = self.factory.post('/api/region/', duplicate_data, format='json')
        response = self.view(request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], "Region with this name or exact latitude and longitude already exists.")
    
    def test_delete_region_success(self):
        """Test successful deletion of a region"""
        request = self.factory.delete(f'/api/region?name={self.test_region.name}')
        response = self.view(request)
        
        self.assertEqual(response.status_code, 200)
        self.assertFalse(Region.objects.filter(name=self.test_region.name).exists())
    
    def test_delete_region_missing_name(self):
        """Test error when name parameter is missing for deletion"""
        request = self.factory.delete('/api/region/')
        response = self.view(request)
        
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['message'], "Name is required to identify the Region to delete.")
    
    def test_delete_region_not_found(self):
        """Test error when trying to delete non-existent region"""
        request = self.factory.delete(f'/api/region?name="Non-existent Region"')
        response = self.view(request)
        
        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.data['message'], "Region with this name does not exist.")
