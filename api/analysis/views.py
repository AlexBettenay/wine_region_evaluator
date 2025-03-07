# In api/views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from main.lib.climate_analyzation import analyze_seasonal_suitability, analyze_longterm_viability, analyze_historical_performance
from main.models import ClimateReading, Region

class WineRegionSeasonAnalysisView(APIView):
    def get(self, request):
        """
        GET request used for fetching long-term viability analysis of Regions.
        
        Supports multiple regions by repeating the 'region' parameter:
        /api/analysis/season?region=Region1&region=Region2&region=Region3

        If no regions are provided, all regions will be compared.
        """

        # Get regions from query params, if none are provided, get all regions
        regions_query = request.query_params.getlist('region')
        if regions_query:
            regions = Region.objects.filter(name__in=regions_query)
        else:
            regions = Region.objects.all()

        if len(regions) == 0:
            return Response({"message": "No regions found."}, status=404)

        results = []
        for region in regions:
            results.append({
                "name": region.name,
                "best_growing_season": analyze_seasonal_suitability(region)
                })
        return Response(results)
    
class WineRegionViabilityAnalysisView(APIView):
    def get(self, request):
        """
        GET request used for fetching long-term viability analysis of Regions.
        
        Supports multiple regions by repeating the 'region' parameter:
        /api/analysis/viability?region=Region1&region=Region2&region=Region3

        If no regions are provided, all regions will be compared.
        """
        # Get regions from query params, if none are provided, get all regions
        regions_query = request.query_params.getlist('region')
        if regions_query:
            regions = Region.objects.filter(name__in=regions_query)
        else:
            regions = Region.objects.all()

        if len(regions) == 0:
            return Response({"message": "No regions found."}, status=404)

        results = []
        for region in regions:
            results.append({
                "name": region.name,
                "longterm_viability": analyze_longterm_viability(region)
                })
        return Response(results)
    
class WineRegionPerformanceComparisonView(APIView):
    def get(self, request):
        """
        GET request used for comparing the historical performance of Regions.
        
        Supports multiple regions by repeating the 'region' parameter:
        /api/analysis/comparison?region=Region1&region=Region2&region=Region3

        If no regions are provided, all regions will be compared.
        """
        # Get regions from query params, if none are provided, get all regions
        regions_query = request.query_params.getlist('region')

        only = request.query_params.get('only')

        if regions_query:
            regions = Region.objects.filter(name__in=regions_query)
        else:
            regions = Region.objects.all()

        if len(regions) == 0:
            return Response({"message": "No regions found."}, status=404)

        results = analyze_historical_performance(regions, only)
        
        return Response(data=results, status=200)