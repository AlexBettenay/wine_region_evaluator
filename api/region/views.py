from rest_framework.views import APIView
from rest_framework.response import Response
from main.models import Region
from django.db import IntegrityError
from .serializers import RegionSerializer
from main.lib.open_meteo import ClimateDataProvider
from datetime import date, timedelta
from main.lib.climate_data_functions import process_climate_data, create_climate_readings

# None of these API endpoints are entirely required but I have added them for the sake of completeness.

class RegionView(APIView):
    def get(self, request):
        """
        GET request used for fetching Region data.

        Accepts query parameter 'name' to identify the Region to fetch.
        """
        name = request.query_params.get('name')

        if not name:
            return Response({"message": "Name is required to identify the Region."}, status=400)
        
        region = Region.objects.get(name=name)
        _serializer = RegionSerializer(region)

        return Response(data=_serializer.data, status=200)
    
    def post(self, request):
        """
        POST request used for creating new Region entry.
        This also fetches and processes climate data for the Region.
        """
        data = request.data.copy()

        name = data.get("name")
        latitude = data.get("latitude")
        longitude = data.get("longitude")
        description = data.get("description")

        if not name or not latitude or not longitude:
            return Response({"message": "Missing required fields."}, status=400)

        try:
            # Create new Region entry.
            region = Region.objects.create(
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

            reading_objects =  process_climate_data(region, climate_data[f"{latitude},{longitude}"])
            create_climate_readings(reading_objects)

        except IntegrityError:
            return Response({"message": "Region with this name or exact latitude and longitude already exists."}, status=400)

        return Response(status=200)

    def delete(self, request):
        """
        DELETE request used for deleting Region entry.

        Accepts query parameter 'name' to identify the Region to delete
        """
        name = request.query_params.get('name')
        
        if not name:
            return Response({"message": "Name is required to identify the Region to delete."}, status=400)
        
        try:
            # Find and delete the Region entry
            region = Region.objects.get(name=name)
            region.delete()
            return Response(status=200)
        except Region.DoesNotExist:
            return Response({"message": "Region with this name does not exist."}, status=404)