from django.db import models
from .location import Location

class ClimateReading(models.Model):
    location = models.ForeignKey(Location, on_delete=models.CASCADE)
    date = models.DateField()
    mean_temperature = models.FloatField()
    max_temperature = models.FloatField()
    min_temperature = models.FloatField()
    min_humidity = models.FloatField()
    max_humidity = models.FloatField()
    mean_humidity = models.FloatField()
    rain = models.FloatField()
    cloud_cover = models.FloatField()
    soil_moisture = models.FloatField()

    class Meta:
        unique_together = ['location', 'date']
        indexes = [
            models.Index(fields=['location', 'date']),
        ]