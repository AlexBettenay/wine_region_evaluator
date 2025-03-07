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
    
    def evaluate(self) -> float:
        """
        Evaluate if climate conditions are optimal for grape growing

        Approach is simplified and could be vastly improved with more data, evaluation criteria and domain knowledge.

        Parameters:
            self (ClimateReading): A model instance containing climate data with
                attributes for max_temperature, mean_humidity, rain and cloud_cover.
        
        Returns:
            float: A score from 0-100 where 100 is perfect growing conditions.
                Score is weighted: temperature (25%), humidity (25%), rainfall (25%) and cloud cover (25%).
        """
        score = 0
        
        # Temperature (between 25C-32C is optimal)
        temp_score = 0
        if 25 <= self.max_temperature <= 32:
            temp_score = 100
        elif 20 <= self.max_temperature < 25:
            temp_score = 80
        elif 32 < self.max_temperature <= 35:
            temp_score = 70
        else:
            temp_score = 40
        
        # Humidity (balanced - not too high or low)
        humidity_score = 0
        if 40 <= self.mean_humidity <= 60:
            humidity_score = 100
        elif 30 <= self.mean_humidity < 40 or 60 < self.mean_humidity <= 70:
            humidity_score = 80
        elif 20 <= self.mean_humidity < 40 or 60 < self.mean_humidity <= 80:
            humidity_score = 60
        else:
            humidity_score = 50
        
        # Rainfall (adquate but not excessive)
        rain_score = 0
        if 0 < self.rain <= 5:
            rain_score = 100
        elif 5 < self.rain <= 15:
            rain_score = 80
        elif self.rain == 0:
            rain_score = 60
        else:
            rain_score = 40

        # Cloud cover (less is better)
        # Cloud cover is represented as a percentage, so we need to invert it
        cloud_score = 100 - self.cloud_cover
        
        # Weigh the factors according to importance (weighting all evenly since I lack the domain knowledge to know which factors effect grape growing the most)
        score = (temp_score * 0.25) + (humidity_score * 0.25) + (rain_score * 0.25) + (cloud_score * 0.25)
        
        return score
