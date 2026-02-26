from rest_framework import serializers
from .models import PlacementDrive

class PlacementDriveSerializer(serializers.ModelSerializer):

    class Meta:
        model = PlacementDrive
        fields = '__all__'
        read_only_fields = ['company']