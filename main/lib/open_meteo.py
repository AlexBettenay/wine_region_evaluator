import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from typing import List, Dict
from openmeteo_sdk import WeatherApiResponse

class ClimateDataProvider:
    """Class to handle fetching and processing climate data from Open-Meteo API"""
    
    def __init__(self, cache_duration=3600):
        """Initialize the climate data provider with cache configuration
        
        Parameters:
            cache_duration: Cache duration in seconds (default: 1 hour)
        """
        # Setup the API client with cache and retry
        cache_session = requests_cache.CachedSession('.cache', expire_after=cache_duration)
        retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
        self.client = openmeteo_requests.Client(session=retry_session)
        
    def get_climate_data(self, latitude: float, longitude: float, start_date: str, end_date: str, variables: List[str]=None) -> Dict[str, pd.DataFrame]:
        """Fetch climate data for one or multiple Regions
        
        Parameters:
            latitude: Region latitude or list of latitudes
            longitude: Region longitude or list of longitudes
            start_date: Start date in YYYY-MM-DD format
            end_date: End date in YYYY-MM-DD format
            variables: List of weather variables to fetch (optional)
            
        Returns:
            Dictionary of pandas DataFrames keyed by region coordinates,
        """
        
        if variables is None:
            variables = ["temperature_2m_mean", "temperature_2m_max", "temperature_2m_min", "cloud_cover_mean",
                         "relative_humidity_2m_mean", "relative_humidity_2m_max", "relative_humidity_2m_min",
                         "precipitation_sum", "soil_moisture_0_to_10cm_mean"]
            
        # Convert single values to lists if needed
        lats = [latitude] if not isinstance(latitude, list) else latitude
        lons = [longitude] if not isinstance(longitude, list) else longitude
        
        # Ensure both lists have the same length
        if len(lats) != len(lons):
            raise ValueError("Latitude and longitude lists must have the same length")
        
        results = {}
        
        # Process each region
        for lat, lon in zip(lats, lons):
            # Configure API request parameters
            params = {
                "latitude": lat,
                "longitude": lon,
                "start_date": start_date,
                "end_date": end_date,
                "models": "MRI_AGCM3_2_S",
                "daily": variables
            }
            
            # Make API request
            url = "https://climate-api.open-meteo.com/v1/climate"
            responses = self.client.weather_api(url, params=params)
            
            # Process the response
            region_key = f"{lat},{lon}"
            results[region_key] = self._process_response(responses[0], variables)
        
        return results
    
    def _process_response(self, response: WeatherApiResponse, variables: List[str]) -> pd.DataFrame:
        """Process API response into a pandas DataFrame
        
        Parameters:
            response: API response object
            variables: List of requested variables
        Returns:
            Pandas DataFrame with processed climate data
        """
        # Get daily data
        daily = response.Daily()
        
        # Create date range
        daily_data = {"date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )}
        
        # Process each variable
        for i, var_name in enumerate(variables):
            daily_data[var_name] = daily.Variables(i).ValuesAsNumpy()
        
        # Create DataFrame
        return pd.DataFrame(data=daily_data)