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