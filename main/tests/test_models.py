from django.test import TestCase
from main.models import Region, ClimateReading
from django.db import IntegrityError

class RegionTestCases(TestCase):
    
    def setUp(self):
        """Create a test region that can be used by multiple tests"""
        self.test_name = "Test Region"
        self.test_lat = 0.0
        self.test_long = 0.0
        self.test_desc = "Test Description"
        
        self.region = Region.objects.create(
            name=self.test_name,
            latitude=self.test_lat,
            longitude=self.test_long,
            description=self.test_desc
        )

    def test_model_creation(self):
        """Test that region attributes match what we provided"""
        self.assertEqual(self.region.name, self.test_name)
        self.assertEqual(self.region.latitude, self.test_lat)
        self.assertEqual(self.region.longitude, self.test_long)
        self.assertEqual(self.region.description, self.test_desc)

    def test_model_creation_name_conflict(self):
        """Test that unique constraint on name works"""
        with self.assertRaises(IntegrityError):
            Region.objects.create(
                name=self.test_name,  # Same name will cause conflict
                latitude=1.0,
                longitude=1.0,
                description="Another Description"
            )

    def test_model_lat_long_conflict(self):
        """Test that unique constraint on lat/long works"""
        with self.assertRaises(IntegrityError):
            Region.objects.create(
                name="Another Name",
                latitude=self.test_lat,  # Same lat/long will cause conflict
                longitude=self.test_long,
                description="Another Description"
            )

    def test_model_get(self):
        """Test retrieving region by name"""
        retrieved_region = Region.objects.get(name=self.test_name)
        self.assertEqual(self.region.name, retrieved_region.name)
        self.assertEqual(self.region.latitude, retrieved_region.latitude)
        self.assertEqual(self.region.longitude, retrieved_region.longitude)
        self.assertEqual(self.region.description, retrieved_region.description)

    def test_model_not_found(self):
        """Test that trying to get a non-existent region raises an exception"""
        with self.assertRaises(Region.DoesNotExist):
            Region.objects.get(name="Non-existent Region")

    def test_model_deletion(self):
        """Test deleting a region"""
        self.region.delete()
        self.assertEqual(Region.objects.filter(name=self.test_name).count(), 0)

class ClimateReadingTestCases(TestCase):

    def setUp(self):
        """Create a test region and associated climate readings"""
        self.test_name = "Test Region"
        self.test_lat = 0.0
        self.test_long = 0.0
        self.test_desc = "Test Description"
        
        self.region = Region.objects.create(
            name=self.test_name,
            latitude=self.test_lat,
            longitude=self.test_long,
            description=self.test_desc
        )
        
        self.reading = ClimateReading.objects.create(
            region=self.region,
            date="2020-01-01",
            mean_temperature=10.0,
            max_temperature=20.0,
            min_temperature=0.0,
            mean_humidity=50.0,
            max_humidity=100.0,
            min_humidity=0.0,
            rain=0.0,
            cloud_cover=0.0,
            soil_moisture=0.0
        )

    def test_model_creation(self):
        """Test that climate reading attributes match what we provided"""
        self.assertEqual(self.reading.region, self.region)
        self.assertEqual(self.reading.date, "2020-01-01")
        self.assertEqual(self.reading.mean_temperature, 10.0)
        self.assertEqual(self.reading.max_temperature, 20.0)
        self.assertEqual(self.reading.min_temperature, 0.0)
        self.assertEqual(self.reading.mean_humidity, 50.0)
        self.assertEqual(self.reading.max_humidity, 100.0)
        self.assertEqual(self.reading.min_humidity, 0.0)
        self.assertEqual(self.reading.rain, 0.0)
        self.assertEqual(self.reading.cloud_cover, 0.0)
        self.assertEqual(self.reading.soil_moisture, 0.0)

    def test_model_deletion(self):
        """Test deleting a climate reading"""
        self.reading.delete()
        self.assertEqual(ClimateReading.objects.filter(region=self.region).count(), 0)
        
        # Ensure region still exists
        self.assertEqual(Region.objects.filter(name=self.test_name).count(), 1)

    def test_model_deletion_region(self):
        """Test deleting a region deletes associated climate readings"""
        region_id = self.region.id  # Store the ID before deletion
        self.region.delete()
        self.assertEqual(Region.objects.filter(name=self.test_name).count(), 0)
        self.assertEqual(ClimateReading.objects.filter(region_id=region_id).count(), 0)

    def test_evaluate_optimal_conditions(self):
        """Test evaluation with optimal growing conditions"""
        optimal_reading = ClimateReading.objects.create(
            region=self.region,
            date="2020-02-01",
            mean_temperature=28.0,
            max_temperature=30.0,  # Optimal: 25-32°C
            min_temperature=24.0,
            mean_humidity=50.0,    # Optimal: 40-60%
            max_humidity=60.0,
            min_humidity=40.0,
            rain=3.0,              # Optimal: 0-5mm
            cloud_cover=15.0,      # Lower is better
            soil_moisture=0.3
        )
        
        score = optimal_reading.evaluate()
        # Should be close to 100 - 25% temp(100) + 25% humidity(100) + 25% rain(100) + 25% cloud(85)
        self.assertGreaterEqual(score, 95)
    
    def test_evaluate_poor_conditions(self):
        """Test evaluation with poor growing conditions"""
        poor_reading = ClimateReading.objects.create(
            region=self.region,
            date="2020-02-02",
            mean_temperature=10.0,
            max_temperature=15.0,  # Poor: < 20°C
            min_temperature=5.0,
            mean_humidity=85.0,    # Poor: > 80%
            max_humidity=90.0,
            min_humidity=80.0,
            rain=25.0,             # Poor: > 15mm
            cloud_cover=90.0,      # High cloud cover
            soil_moisture=0.5
        )
        
        score = poor_reading.evaluate()
        # Expected: 25% temp(40) + 25% humidity(50) + 25% rain(40) + 25% cloud(10) = 35
        self.assertLessEqual(score, 40)
    
    def test_evaluate_mixed_conditions(self):
        """Test evaluation with mixed growing conditions"""
        mixed_reading = ClimateReading.objects.create(
            region=self.region,
            date="2020-02-03",
            mean_temperature=23.0,
            max_temperature=24.0,  # Good but not optimal: 80 points
            min_temperature=18.0,
            mean_humidity=65.0,    # Good but not optimal: 80 points
            max_humidity=70.0,
            min_humidity=60.0,
            rain=2.0,              # Optimal: 100 points
            cloud_cover=40.0,      # Moderate: 60 points
            soil_moisture=0.3
        )
        
        score = mixed_reading.evaluate()
        # Expected: 25% temp(80) + 25% humidity(80) + 25% rain(100) + 25% cloud(60) = 80
        self.assertTrue(75 <= score <= 85)
    
    def test_evaluate_boundary_conditions(self):
        """Test evaluation with boundary conditions"""
        boundary_reading = ClimateReading.objects.create(
            region=self.region,
            date="2020-02-04",
            mean_temperature=25.0,
            max_temperature=25.0,  # Lower boundary of optimal: 100 points
            min_temperature=20.0,
            mean_humidity=40.0,    # Lower boundary of optimal: 100 points
            max_humidity=50.0,
            min_humidity=30.0,
            rain=5.0,              # Upper boundary of optimal: 100 points
            cloud_cover=0.0,       # Best possible: 100 points
            soil_moisture=0.3
        )
        
        score = boundary_reading.evaluate()
        # Expected: 25% temp(100) + 25% humidity(100) + 25% rain(100) + 25% cloud(100) = 100
        self.assertEqual(score, 100)
    
    def test_evaluate_zero_rainfall(self):
        """Test evaluation with zero rainfall"""
        zero_rain_reading = ClimateReading.objects.create(
            region=self.region,
            date="2020-02-05",
            mean_temperature=28.0,
            max_temperature=30.0,  # Optimal: 100 points
            min_temperature=25.0,
            mean_humidity=50.0,    # Optimal: 100 points
            max_humidity=60.0,
            min_humidity=40.0,
            rain=0.0,              # Zero rain: 60 points
            cloud_cover=30.0,      # 70 points
            soil_moisture=0.3
        )
        
        score = zero_rain_reading.evaluate()
        # Expected: 25% temp(100) + 25% humidity(100) + 25% rain(60) + 25% cloud(70) = 82.5
        self.assertAlmostEqual(score, 82.5, delta=0.5)