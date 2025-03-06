from celery import shared_task
from main.lib.open_meteo import ClimateDataProvider
from main.models import ClimateReading
from datetime import date, timedelta

from main.lib.climate_data_functions import get_all_location_coordinates, process_climate_data, determine_start_date, create_climate_readings

@shared_task
def fetch_data():
    """Main task to fetch and process climate data

    This task fetches climate data for all locations and processes it.
    NOTE: Always fetches data from yesterday to ensure completeness.
    """
    
    # Get location data
    latitudes, longitudes, location_lookup, locations = get_all_location_coordinates()

    yesterday = date.today() - timedelta(days=1)
    from_date = determine_start_date(locations)

    if from_date >= yesterday:
        return "No new data to fetch"
    
    # Fetch climate data
    provider = ClimateDataProvider()
    climate_data = provider.get_climate_data(
        latitude=latitudes,
        longitude=longitudes,
        start_date=determine_start_date(locations).strftime("%Y-%m-%d"),
        end_date=yesterday.strftime("%Y-%m-%d")
    )
    
    # Process each location's data
    reading_objects = []
    for coord_key, df in climate_data.items():
        location = location_lookup[coord_key]
        reading_objects.extend(process_climate_data(location, df))

    create_climate_readings(reading_objects)
        
    return "Data processing complete"