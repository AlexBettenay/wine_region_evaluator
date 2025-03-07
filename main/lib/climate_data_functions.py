from main.models import Region, ClimateReading
from datetime import date
from django.db.models import Max
from typing import List
import pandas as pd

def get_all_region_coordinates():
    """
    Get coordinates for all Regions and build lookup dictionary

    Returns:
        Tuple: (latitudes: (List[float]), longitudes: (List[float]), lookup_dict: (Dict[str, Region]), regions: (List[Region])
    """
    regions = Region.objects.all()
    latitudes = []
    longitudes = []
    lookup_dict = {}
    
    for region in regions:
        latitudes.append(region.latitude)
        longitudes.append(region.longitude)
        lookup_dict[f"{region.latitude},{region.longitude}"] = region
    
    return latitudes, longitudes, lookup_dict, regions

def process_climate_data(region: Region, climate_data: pd.DataFrame) -> List[ClimateReading]:
    """
    Process climate data for a specific region

    Parameters:
        region (Region): A Region model instance
        climate_data (DataFrame): A DataFrame containing climate data for the Region
    """
    # Add your processing logic here
    print(f"Processing data for {region.name}")

    readings = []
    # Iterate through each row (day) in the DataFrame
    for index, row in climate_data.iterrows():
        # Create a new climate reading for each day
        reading = ClimateReading(
            region=region,
            date=row['date'],
            mean_temperature=row['temperature_2m_mean'],
            max_temperature=row['temperature_2m_max'],
            min_temperature=row['temperature_2m_min'],
            mean_humidity=row['relative_humidity_2m_mean'],
            max_humidity=row['relative_humidity_2m_max'],
            min_humidity=row['relative_humidity_2m_min'],
            rain=row['precipitation_sum'],
            cloud_cover=row['cloud_cover_mean'],
            soil_moisture=row['soil_moisture_0_to_10cm_mean']
        )
        readings.append(reading)
    return readings

def determine_start_date(regions: List[Region]) -> date:
    """Determine the start date for fetching climate data
    
    Gets the latest reading date for each region,
    then returns the earliest of these dates to ensure all regions get updated.

    Parameters:
        regions (List[Region]): List of Region instances
    """
    # Get the latest date for each Region
    latest_dates = ClimateReading.objects.filter(region__in=regions).values('region').annotate(
        latest_date=Max('date')
    )
    
    if latest_dates.exists():
        # Find the earliest date among all the latest dates
        earliest_of_latest = min(item['latest_date'] for item in latest_dates)
        
        return earliest_of_latest
    
    # Default to 30 years ago
    today = date.today()
    return date(today.year - 1, today.month, today.day)

def create_climate_readings(reading_objects: List[ClimateReading]):
    """
    Bulk create ClimateReading objects

    Parameters:
        reading_objects (List[ClimateReading]): List of ClimateReading objects to create
    
    """
    if (len(reading_objects) > 0):
        # Bulk create the ClimateReading objects
        ClimateReading.objects.bulk_create(reading_objects, ignore_conflicts=True)