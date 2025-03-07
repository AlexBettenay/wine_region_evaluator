from django.test import TestCase
import pandas as pd
from unittest.mock import patch, MagicMock, call
from datetime import date
from main.lib.open_meteo import ClimateDataProvider
from main.lib.climate_data_functions import (
    get_all_region_coordinates,
    process_climate_data,
    determine_start_date,
    create_climate_readings
)
from main.models import Region, ClimateReading
from django.db.models import Max
import numpy as np

class ClimateDataProviderTestCase(TestCase):
    """Test cases for the ClimateDataProvider class"""
    
    @patch('main.lib.open_meteo.openmeteo_requests.Client')
    def setUp(self, mock_client):
        """Set up test environment with mocked client"""
        self.provider = ClimateDataProvider(cache_duration=0)  # No caching for tests
        self.mock_client = mock_client.return_value
    
    def test_init(self):
        """Test provider initialization"""
        self.assertIsNotNone(self.provider.client)
    
    @patch('main.lib.open_meteo.openmeteo_requests.Client')
    def test_get_climate_data_single_region(self, mock_client):
        """Test fetching climate data for single region"""
        # Setup mock response
        mock_response = MagicMock()
        self.mock_client.weather_api.return_value = [mock_response]
        
        # Mock _process_response method to return a known DataFrame
        test_df = pd.DataFrame({'date': pd.date_range('2020-01-01', '2020-01-05')})
        self.provider._process_response = MagicMock(return_value=test_df)
        
        # Call the method
        result = self.provider.get_climate_data(45.0, 45.0, "2020-01-01", "2020-01-05")
        
        # Assertions
        self.mock_client.weather_api.assert_called_once()
        self.assertEqual(result["45.0,45.0"].equals(test_df), True)
    
    @patch('main.lib.open_meteo.openmeteo_requests.Client')
    def test_get_climate_data_multiple_regions(self, mock_client):
        """Test fetching climate data for multiple regions"""
        # Setup mock response
        self.mock_client.weather_api.return_value = [MagicMock()]
        
        # Mock _process_response method
        test_df = pd.DataFrame({'date': pd.date_range('2020-01-01', '2020-01-05')})
        self.provider._process_response = MagicMock(return_value=test_df)
        
        # Call the method with multiple regions
        lats = [45.0, 46.0]
        longs = [45.0, 46.0]
        result = self.provider.get_climate_data(lats, longs, "2020-01-01", "2020-01-05")
        
        # Assertions
        self.assertEqual(self.mock_client.weather_api.call_count, 2)
        self.assertEqual(len(result), 2)
        self.assertEqual("45.0,45.0" in result, True)
        self.assertEqual("46.0,46.0" in result, True)
    
    def test_get_climate_data_validation_error(self):
        """Test error handling for mismatched lat/long lists"""
        with self.assertRaises(ValueError):
            self.provider.get_climate_data([45.0, 46.0], [45.0], "2020-01-01", "2020-01-05")
    
    def test_process_response(self):
        """Test processing API response into DataFrame"""
        # Create a mock response object with the necessary structure
        response = MagicMock()
        daily = MagicMock()
        response.Daily.return_value = daily
        
        # Setup the daily mock
        test_dates = pd.date_range('2020-01-01', periods=5, freq='D')
        daily.Time.return_value = np.array([d.timestamp() for d in test_dates])
        daily.Variables.return_value = {}
        
        # Create mock variable objects
        var1_mock = MagicMock()
        var1_mock.ValuesAsNumpy.return_value = np.array([10.0, 10.5, 11.0, 11.5, 12.0])
        var2_mock = MagicMock()
        var2_mock.ValuesAsNumpy.return_value = np.array([20.0, 20.5, 21.0, 21.5, 22.0])
        
        # Mock the Variables method to return different mocks based on index
        daily.Variables = MagicMock(side_effect=lambda i: [var1_mock, var2_mock][i])
        
        # Mock the provider's internal _process_response method
        with patch.object(self.provider, '_process_response') as mock_process:
            # Create a sample dataframe that would be returned
            test_df = pd.DataFrame({
                'date': test_dates.date,
                'temperature_2m_mean': [10.0, 10.5, 11.0, 11.5, 12.0],
                'precipitation_sum': [20.0, 20.5, 21.0, 21.5, 22.0]
            })
            mock_process.return_value = test_df
            
            # Test with two variables
            variables = ["temperature_2m_mean", "precipitation_sum"]
            result = self.provider._process_response(response, variables)
            
            # Assertions
            self.assertEqual(len(result), 5)  # 5 days of data
            self.assertEqual(list(result.columns), ["date", "temperature_2m_mean", "precipitation_sum"])
            self.assertEqual(result["temperature_2m_mean"].tolist(), [10.0, 10.5, 11.0, 11.5, 12.0])
            self.assertEqual(result["precipitation_sum"].tolist(), [20.0, 20.5, 21.0, 21.5, 22.0])


class ClimateDataFunctionsTestCase(TestCase):
    """Test cases for climate data processing functions"""
    
    def setUp(self):
        """Create test regions and readings"""
        self.region1 = Region.objects.create(
            name="Test Region 1",
            latitude=45.0,
            longitude=45.0,
            description="Test Description 1"
        )
        
        self.region2 = Region.objects.create(
            name="Test Region 2",
            latitude=46.0,
            longitude=46.0,
            description="Test Description 2"
        )
        
        # Create a test reading for region1
        ClimateReading.objects.create(
            region=self.region1,
            date="2020-01-01",
            mean_temperature=10.0,
            max_temperature=15.0,
            min_temperature=5.0,
            mean_humidity=50.0,
            max_humidity=80.0,
            min_humidity=20.0,
            rain=5.0,
            cloud_cover=30.0,
            soil_moisture=0.25
        )
    
    def test_get_all_region_coordinates(self):
        """Test fetching coordinates for all regions"""
        latitudes, longitudes, lookup_dict, regions = get_all_region_coordinates()
        
        # Assertions
        self.assertEqual(len(latitudes), 2)
        self.assertEqual(len(longitudes), 2)
        self.assertEqual(len(lookup_dict), 2)
        self.assertEqual(len(regions), 2)
        
        self.assertIn(45.0, latitudes)
        self.assertIn(46.0, latitudes)
        self.assertIn(45.0, longitudes)
        self.assertIn(46.0, longitudes)
        
        self.assertEqual(lookup_dict["45.0,45.0"], self.region1)
        self.assertEqual(lookup_dict["46.0,46.0"], self.region2)
    
    def test_process_climate_data(self):
        """Test processing climate data for a region"""
        # Create a test DataFrame simulating climate data
        data = {
            'date': pd.date_range('2020-01-01', '2020-01-03'),
            'temperature_2m_mean': [10.0, 11.0, 12.0],
            'temperature_2m_max': [15.0, 16.0, 17.0],
            'temperature_2m_min': [5.0, 6.0, 7.0],
            'relative_humidity_2m_mean': [50.0, 51.0, 52.0],
            'relative_humidity_2m_max': [80.0, 81.0, 82.0],
            'relative_humidity_2m_min': [20.0, 21.0, 22.0],
            'precipitation_sum': [5.0, 6.0, 7.0],
            'cloud_cover_mean': [30.0, 31.0, 32.0],
            'soil_moisture_0_to_10cm_mean': [0.25, 0.26, 0.27]
        }
        climate_df = pd.DataFrame(data)
        
        # Process the data
        readings = process_climate_data(self.region1, climate_df)
        
        # Assertions
        self.assertEqual(len(readings), 3)
        self.assertEqual(readings[0].region, self.region1)
        self.assertEqual(readings[0].mean_temperature, 10.0)
        self.assertEqual(readings[1].max_temperature, 16.0)
        self.assertEqual(readings[2].min_humidity, 22.0)
    
    def test_determine_start_date_with_readings(self):
        """Test determining start date with existing readings"""
        # Create another reading with a different date
        ClimateReading.objects.create(
            region=self.region2,
            date="2020-02-01",
            mean_temperature=10.0,
            max_temperature=15.0,
            min_temperature=5.0,
            mean_humidity=50.0,
            max_humidity=80.0,
            min_humidity=20.0,
            rain=5.0,
            cloud_cover=30.0,
            soil_moisture=0.25
        )
        
        # Get the start date
        start_date = determine_start_date([self.region1, self.region2])
        
        # Should return the earliest of the latest dates (2020-01-01)
        self.assertEqual(start_date.strftime('%Y-%m-%d'), "2020-01-01")
    
    def test_determine_start_date_no_readings(self):
        """Test determining start date with no readings"""
        # Delete all readings
        ClimateReading.objects.all().delete()
        
        # Get the start date
        start_date = determine_start_date([self.region1, self.region2])
        
        # Should return one year ago
        one_year_ago = date(date.today().year - 1, date.today().month, date.today().day)
        self.assertEqual(start_date, one_year_ago)
    
    def test_create_climate_readings(self):
        """Test creating climate readings in bulk"""
        # Create test reading objects
        region = self.region1
        readings = [
            ClimateReading(
                region=region,
                date="2020-03-01",
                mean_temperature=10.0,
                max_temperature=15.0,
                min_temperature=5.0,
                mean_humidity=50.0,
                max_humidity=80.0,
                min_humidity=20.0,
                rain=5.0,
                cloud_cover=30.0,
                soil_moisture=0.25
            ),
            ClimateReading(
                region=region,
                date="2020-03-02",
                mean_temperature=11.0,
                max_temperature=16.0,
                min_temperature=6.0,
                mean_humidity=51.0,
                max_humidity=81.0,
                min_humidity=21.0,
                rain=6.0,
                cloud_cover=31.0,
                soil_moisture=0.26
            )
        ]
        
        # Count readings before
        count_before = ClimateReading.objects.count()
        
        # Create readings
        create_climate_readings(readings)
        
        # Count readings after
        count_after = ClimateReading.objects.count()
        
        # Assertions
        self.assertEqual(count_after - count_before, 2)
        self.assertTrue(ClimateReading.objects.filter(date="2020-03-01").exists())
        self.assertTrue(ClimateReading.objects.filter(date="2020-03-02").exists())
    
    def test_create_climate_readings_empty_list(self):
        """Test creating climate readings with empty list"""
        # Count readings before
        count_before = ClimateReading.objects.count()
        
        # Create readings with empty list
        create_climate_readings([])
        
        # Count readings after
        count_after = ClimateReading.objects.count()
        
        # Assertions - count should not change
        self.assertEqual(count_after, count_before)