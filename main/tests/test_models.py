from django.test import TestCase
from main.models import Location, ClimateReading
from django.db import IntegrityError

class LocationTestCases(TestCase):
    
    def setUp(self):
        """Create a test location that can be used by multiple tests"""
        self.test_name = "Test Location"
        self.test_lat = 0.0
        self.test_long = 0.0
        self.test_desc = "Test Description"
        
        self.location = Location.objects.create(
            name=self.test_name,
            latitude=self.test_lat,
            longitude=self.test_long,
            description=self.test_desc
        )

    def test_model_creation(self):
        """Test that location attributes match what we provided"""
        self.assertEqual(self.location.name, self.test_name)
        self.assertEqual(self.location.latitude, self.test_lat)
        self.assertEqual(self.location.longitude, self.test_long)
        self.assertEqual(self.location.description, self.test_desc)

    def test_model_creation_name_conflict(self):
        """Test that unique constraint on name works"""
        with self.assertRaises(IntegrityError):
            Location.objects.create(
                name=self.test_name,  # Same name will cause conflict
                latitude=1.0,
                longitude=1.0,
                description="Another Description"
            )

    def test_model_lat_long_conflict(self):
        """Test that unique constraint on lat/long works"""
        with self.assertRaises(IntegrityError):
            Location.objects.create(
                name="Another Name",
                latitude=self.test_lat,  # Same lat/long will cause conflict
                longitude=self.test_long,
                description="Another Description"
            )

    def test_model_get(self):
        """Test retrieving location by name"""
        retrieved_location = Location.objects.get(name=self.test_name)
        self.assertEqual(self.location.name, retrieved_location.name)
        self.assertEqual(self.location.latitude, retrieved_location.latitude)
        self.assertEqual(self.location.longitude, retrieved_location.longitude)
        self.assertEqual(self.location.description, retrieved_location.description)

    def test_model_not_found(self):
        """Test that trying to get a non-existent location raises an exception"""
        with self.assertRaises(Location.DoesNotExist):
            Location.objects.get(name="Non-existent Location")

    def test_model_deletion(self):
        """Test deleting a location"""
        self.location.delete()
        self.assertEqual(Location.objects.filter(name=self.test_name).count(), 0)

class ClimateReadingTestCases(TestCase):

    def setUp(self):
        """Create a test location and associated climate readings"""
        self.test_name = "Test Location"
        self.test_lat = 0.0
        self.test_long = 0.0
        self.test_desc = "Test Description"
        
        self.location = Location.objects.create(
            name=self.test_name,
            latitude=self.test_lat,
            longitude=self.test_long,
            description=self.test_desc
        )
        
        self.reading = ClimateReading.objects.create(
            location=self.location,
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
        self.assertEqual(self.reading.location, self.location)
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
        self.assertEqual(ClimateReading.objects.filter(location=self.location).count(), 0)
        
        # Ensure location still exists
        self.assertEqual(Location.objects.filter(name=self.test_name).count(), 1)

    def test_model_deletion_location(self):
        """Test deleting a location deletes associated climate readings"""
        location_id = self.location.id  # Store the ID before deletion
        self.location.delete()
        self.assertEqual(Location.objects.filter(name=self.test_name).count(), 0)
        self.assertEqual(ClimateReading.objects.filter(location_id=location_id).count(), 0)