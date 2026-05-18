from rest_framework import serializers
from django.utils import timezone
from .models import PlacementDrive

class PlacementDriveSerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='company.companyprofile.company_name', read_only=True)
    company_username = serializers.CharField(source='company.username', read_only=True)
    required_skills = serializers.CharField(required=False, allow_blank=True)

    class Meta:
        model = PlacementDrive
        fields = '__all__'
        read_only_fields = ['company']

    def validate_application_deadline(self, value):
        if value < timezone.localdate():
            raise serializers.ValidationError("Application deadline cannot be in the past.")
        return value

    def validate_openings(self, value):
        if value < 1:
            raise serializers.ValidationError("Openings must be at least 1.")
        return value

    def validate_ctc(self, value):
        if value is not None and value < 0:
            raise serializers.ValidationError("CTC cannot be negative.")
        return value

    def to_representation(self, instance):
        rep = super().to_representation(instance)
        rep['required_skills'] = ", ".join(instance.required_skills.values_list('name', flat=True))
        return rep

    def create(self, validated_data):
        required_skills_str = validated_data.pop('required_skills', '')
        drive = super().create(validated_data)
        self._save_skills(drive, required_skills_str)
        return drive

    def update(self, instance, validated_data):
        required_skills_str = validated_data.pop('required_skills', None)
        drive = super().update(instance, validated_data)
        if required_skills_str is not None:
            self._save_skills(drive, required_skills_str)
        return drive

    def _save_skills(self, drive, skills_str):
        from users.models import Skill
        skills_list = []
        if skills_str:
            skill_names = [s.strip() for s in skills_str.split(',') if s.strip()]
            for name in skill_names:
                skill, created = Skill.objects.get_or_create(name=name)
                skills_list.append(skill)
        drive.required_skills.set(skills_list)

