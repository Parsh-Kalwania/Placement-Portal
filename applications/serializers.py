from rest_framework import serializers
from .models import Application


class ApplicationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Application
        fields = "__all__"
        read_only_fields = ["student", "status"]
        
class PlacementHistorySerializer(serializers.ModelSerializer):
    job_title = serializers.CharField(source='drive.job_title', read_only=True)
    company_name = serializers.CharField(source='drive.company.companyprofile.company_name', read_only=True)
    application_date = serializers.DateTimeField(source='applied_at', read_only=True)

    class Meta:
        model = Application
        fields = [
            'job_title',
            'company_name',
            'application_date',
            'status'
        ]