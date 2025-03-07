from django.db import models

class Region(models.Model):
    name = models.CharField(max_length=255, unique=True)
    latitude = models.FloatField(null=False)
    longitude = models.FloatField(null=False)
    description = models.TextField(null=True, blank=True)

    class Meta:
        unique_together = ['latitude', 'longitude']
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
        ]