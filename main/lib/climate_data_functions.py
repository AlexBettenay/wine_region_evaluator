from celery import shared_task
from main.lib.open_meteo import ClimateDataProvider
from main.models import Location, ClimateReading
from datetime import date, timedelta
from django.db.models import Max

def get_all_location_coordinates():
    """Get coordinates for all locations and build lookup dictionary"""
    locations = Location.objects.all()
    latitudes = []
    longitudes = []
    lookup_dict = {}
    
    for location in locations:
        latitudes.append(location.latitude)
        longitudes.append(location.longitude)
        lookup_dict[f"{location.latitude},{location.longitude}"] = location
    
    return latitudes, longitudes, lookup_dict, locations

def process_climate_data(location, climate_data):
    """Process climate data for a specific location"""
    # Add your processing logic here
    print(f"Processing data for {location.name}")

    readings = []
    # Iterate through each row (day) in the DataFrame
    for index, row in climate_data.iterrows():
        # Create a new climate reading for each day
        reading = ClimateReading(
            location=location,
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

def determine_start_date(locations):
    """Determine the start date for fetching climate data
    
    Gets the latest reading date for each location,
    then returns the earliest of these dates to ensure all locations get updated.
    """
    # Get the latest date for each location
    latest_dates = ClimateReading.objects.filter(location__in=locations).values('location').annotate(
        latest_date=Max('date')
    )
    
    if latest_dates.exists():
        # Find the earliest date among all the latest dates
        earliest_of_latest = min(item['latest_date'] for item in latest_dates)
        
        return earliest_of_latest
    
    # Default to 30 years ago
    today = date.today()
    return date(today.year - 1, today.month, today.day)

def create_climate_readings(reading_objects):
    """Bulk create ClimateReading objects"""
    if (len(reading_objects) > 0):
        # Bulk create the ClimateReading objects
        ClimateReading.objects.bulk_create(reading_objects, ignore_conflicts=True)