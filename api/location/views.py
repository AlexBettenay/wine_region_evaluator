from rest_framework.views import APIView
from rest_framework.response import Response
from main.models import Location
from django.db import IntegrityError
from .serializers import LocationSerializer
from main.lib.open_meteo import ClimateDataProvider
from datetime import date, timedelta
from main.lib.climate_data_functions import get_all_location_coordinates, process_climate_data, determine_start_date, create_climate_readings

# None of these API endpoints are entirely required but I have added them for the sake of completeness.

class LocationView(APIView):
    def get(self, request):
        name = request.query_params.get('name')

        if not name:
            return Response({"message": "Name is required to identify the location."}, status=400)
        
        location = Location.objects.get(name=name)
        _serializer = LocationSerializer(location)

        return Response(data=_serializer.data, status=200)
    
    # POST request used for creating new location entry.
    # This also fetches and processes climate data for the location.
    def post(self, request):
        data = request.data.copy()

        name = data.get("name")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        description = data.get("description")

        if not name or not latitude or not longitude:
            return Response({"message": "Missing required fields."}, status=400)

        try:
            # Create new location entry.
            location = Location.objects.create(
                name=name,
                latitude=latitude,
                longitude=longitude,
                description=description
            )

            provider =  ClimateDataProvider()
            today = date.today()
            start_date = date(today.year - 1, today.month, today.day)
            end_date = date.today() - timedelta(days=1)
            climate_data = provider.get_climate_data(latitude, longitude, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))

            reading_objects =  process_climate_data(location, climate_data[f"{latitude},{longitude}"])
            create_climate_readings(reading_objects)

        except IntegrityError:
            return Response({"message": "Location with this name or exact latitude and longitude already exists."}, status=400)

        return Response(status=200)
    
    # DELETE request used for deleting existing location entry.
    def delete(self, request):
        name = request.query_params.get('name')
        
        if not name:
            return Response({"message": "Name is required to identify the location to delete."}, status=400)
        
        try:
            # Find and delete the location entry
            location = Location.objects.get(name=name)
            location.delete()
            return Response(status=200)
        except Location.DoesNotExist:
            return Response({"message": "Location with this name does not exist."}, status=404)