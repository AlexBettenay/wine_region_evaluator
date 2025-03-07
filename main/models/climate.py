from django.db import models
from .region import Region

class ClimateReading(models.Model):
    region = models.ForeignKey(Region, on_delete=models.CASCADE, related_name='climate_readings')
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
        unique_together = ['region', 'date']
        indexes = [
            models.Index(fields=['region', 'date']),
        ]