from django.db.models import Avg
import pandas as pd
from main.models import ClimateReading, Region
from datetime import date
from typing import List, TypedDict

class RegionIdealSeason(TypedDict):
    name: str
    best_growing_season: List[str]

class RegionViability(TypedDict): 
    name: str
    longterm_viability: float

def evaluate_grape_conditions(climate_reading: ClimateReading) -> float:
    """
    Evaluate if climate conditions are optimal for grape growing

    Approach is simplified and could be vastly improved with more data, evaluation criteria and domain knowledge.

    Parameters:
        climate_reading (ClimateReading): A model instance containing climate data with
            attributes for max_temperature, mean_humidity, rain and cloud_cover.
    
    Returns:
        float: A score from 0-100 where 100 is perfect growing conditions.
            Score is weighted: temperature (25%), humidity (25%), rainfall (25%) and cloud cover (25%).
    """
    score = 0
    
    # Temperature (between 25C-32C is optimal)
    temp_score = 0
    if 25 <= climate_reading.max_temperature <= 32:
        temp_score = 100
    elif 20 <= climate_reading.max_temperature < 25:
        temp_score = 80
    elif 32 < climate_reading.max_temperature <= 35:
        temp_score = 70
    else:
        temp_score = 40
    
    # Humidity (balanced - not too high or low)
    humidity_score = 0
    if 40 <= climate_reading.mean_humidity <= 60:
        humidity_score = 100
    elif 30 <= climate_reading.mean_humidity < 40 or 60 < climate_reading.mean_humidity <= 70:
        humidity_score = 80
    elif 20 <= climate_reading.mean_humidity < 40 or 60 < climate_reading.mean_humidity <= 80:
        humidity_score = 60
    else:
        humidity_score = 50
    
    # Rainfall (adquate but not excessive)
    rain_score = 0
    if 0 < climate_reading.rain <= 5:
        rain_score = 100
    elif 5 < climate_reading.rain <= 15:
        rain_score = 80
    elif climate_reading.rain == 0:
        rain_score = 60
    else:
        rain_score = 40

    # Cloud cover (less is better)
    # Cloud cover is represented as a percentage, so we need to invert it
    cloud_score = 100 - climate_reading.cloud_cover
    
    # Weigh the factors according to importance (weighting all evenly since I lack the domain knowledge to know which factors effect grape growing the most)
    score = (temp_score * 0.25) + (humidity_score * 0.25) + (rain_score * 0.25) + (cloud_score * 0.25)
    
    return score

def analyze_seasonal_suitability(region: Region) -> List[RegionIdealSeason]:
    """
    Determine the best time of year for grape growing in a Region.
    
    Parameters:
        region (Region): A model instance representing a wine growing region with
            associated climate_readings.
    
    Returns:
        A list of Dictionaries (RegionIdealSeason) containing:
                - name (str): Name of the region
                - best_growing_season List(str): The best consecutive 3-month period for grape growing.
    """
    # Get all readings for this region
    readings = region.climate_readings.all()
    
    # Add evaluation score to each reading
    evaluated_readings = []
    for reading in readings:
        score = evaluate_grape_conditions(reading)
        evaluated_readings.append({
            'date': reading.date,
            'month': reading.date.month,
            'score': score
        })
    
    # Convert to DataFrame for analysis
    df = pd.DataFrame(evaluated_readings)
    
    # Calculate average score by month
    monthly_avg = df.groupby('month')['score'].mean().sort_values(ascending=False)
    
    # Identify best consecutive 3-month period (growing season)
    # This is a simplified approach - you could make it more sophisticated
    best_month = monthly_avg.idxmax()
    growing_season = [(best_month + i) % 12 or 12 for i in range(3)]
    
    month_names = {1: 'January', 2: 'February', 3: 'March', 4: 'April', 
                   5: 'May', 6: 'June', 7: 'July', 8: 'August', 
                   9: 'September', 10: 'October', 11: 'November', 12: 'December'}
    
    return [month_names[m] for m in growing_season]

def analyze_longterm_viability(region: Region) -> List[RegionViability]:
    """
    Calculate percentage of time with optimal conditions over last 30 years.

    In a more complete approach, adding a user-defined variables for optimal threshold and time period would be useful.
    
    Parameters:
        region (Region): A model instance representing a wine growing region.
    
    Returns:
        A list of Dictionaries (RegionViability) containing:
                - name (str): Name of the region
                - longterm_viability (float): Percentage (0-100) of days with optimal growing conditions (score >= 70),
            rounded to 2 decimal places. Returns 0 if no climate readings exist.
    """

    thirty_years_ago = date(date.today().year - 30, date.today().month, date.today().day)
    
    # Get readings for this region from the last 30 years
    readings = region.climate_readings.filter(date__gte=thirty_years_ago)
    
    total_days = readings.count()
    if total_days == 0:
        return 0
    
    # Count days with good conditions (score >= 70)
    optimal_days = 0
    for reading in readings:
        score = evaluate_grape_conditions(reading)
        if score >= 70:
            optimal_days += 1
    
    # Calculate percentage
    percentage = (optimal_days / total_days) * 100
    
    return round(percentage, 2)