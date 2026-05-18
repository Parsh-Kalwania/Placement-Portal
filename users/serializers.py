from rest_framework import serializers
import re
from .models import CustomUser, StudentProfile, CompanyProfile


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']


class StudentProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    skills = serializers.SerializerMethodField()
    skills_list = serializers.SerializerMethodField()

    class Meta:
        model = StudentProfile
        fields = '__all__'

    def get_skills(self, obj):
        return ", ".join(obj.skills.values_list('name', flat=True))

    def get_skills_list(self, obj):
        return list(obj.skills.values_list('name', flat=True))

    def update(self, instance, validated_data):
        if hasattr(self, 'initial_data') and 'skills' in self.initial_data:
            skills_str = self.initial_data.get('skills', '').strip()
            from .models import Skill
            skills_list = []
            if skills_str:
                skill_names = [s.strip() for s in skills_str.split(',') if s.strip()]
                for name in skill_names:
                    skill, created = Skill.objects.get_or_create(name=name)
                    skills_list.append(skill)
            instance.skills.set(skills_list)
        return super().update(instance, validated_data)


    def validate_phone(self, value):
        if value and not re.fullmatch(r'^\+?[0-9][0-9\s-]{7,14}$', value):
            raise serializers.ValidationError("Enter a valid phone number.")
        return value

    def validate_cgpa(self, value):
        if value is not None and not 0 <= value <= 10:
            raise serializers.ValidationError("CGPA must be between 0 and 10.")
        return value

    def validate(self, attrs):
        batch_year = attrs.get('batch_year', getattr(self.instance, 'batch_year', None))
        graduation_year = attrs.get('graduation_year', getattr(self.instance, 'graduation_year', None))
        if batch_year and graduation_year and batch_year > graduation_year:
            raise serializers.ValidationError("Batch year cannot be after graduation year.")
        return attrs


class CompanyProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = CompanyProfile
        fields = '__all__'

    def validate_company_name(self, value):
        if not value.strip():
            raise serializers.ValidationError("Company name is required.")
        return value

    def validate_hr_contact(self, value):
        if not value.strip():
            raise serializers.ValidationError("HR contact is required.")
        return value


class AdminCompanySerializer(serializers.ModelSerializer):
    company_name = serializers.CharField(source='companyprofile.company_name', read_only=True)
    hr_contact = serializers.CharField(source='companyprofile.hr_contact', read_only=True)
    website = serializers.CharField(source='companyprofile.website', read_only=True)
    approved_by_username = serializers.CharField(source='approved_by.username', read_only=True)

    class Meta:
        model = CustomUser
        fields = [
            'id',
            'username',
            'email',
            'company_name',
            'hr_contact',
            'website',
            'is_approved',
            'is_blacklisted',
            'approved_by',
            'approved_by_username',
            'approved_at',
        ]
        
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from .models import CustomUser


class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = CustomUser
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = CustomUser.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            password=validated_data['password'],
            role=self.context.get('role')
        )
        return user
