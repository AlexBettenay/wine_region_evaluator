from rest_framework import serializers

class RegionSerializer(serializers.Serializer):
    name = serializers.CharField()
    latitude = serializers.FloatField()
    longitude = serializers.FloatField()
    description = serializers.CharField(required=False)