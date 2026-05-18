from django.db.models import Avg, Count
from users.models import CustomUser, StudentProfile, CompanyProfile, Skill
from drives.models import PlacementDrive
from applications.models import Application

def get_admin_analytics():
    total_students = CustomUser.objects.filter(role='student').count()
    placed_students = Application.objects.filter(status='selected').values('student').distinct().count()
    total_companies = CustomUser.objects.filter(role='company', is_approved=True).count()
    total_drives = PlacementDrive.objects.count()
    
    # Advanced metrics
    active_applications = Application.objects.exclude(status__in=['selected', 'rejected']).count()
    
    avg_salary_agg = PlacementDrive.objects.filter(
        application__status='selected'
    ).aggregate(avg_sal=Avg('ctc'))
    avg_salary = avg_salary_agg['avg_sal'] or 0.0

    return {
        "total_students": total_students,
        "placed_students": placed_students,
        "placement_percentage": round((placed_students / total_students * 100) if total_students > 0 else 0, 1),
        "total_companies": total_companies,
        "total_drives": total_drives,
        "avg_salary": round(avg_salary, 2),
        "active_applications": active_applications,
        "avg_applicants_per_drive": round((Application.objects.count() / total_drives) if total_drives > 0 else 0, 1),
    }

def get_student_analytics(student_user):
    apps = Application.objects.filter(student=student_user)
    total_apps = apps.count()
    selected_apps = apps.filter(status='selected').count()
    rejected_apps = apps.filter(status='rejected').count()
    
    success_rate = round((selected_apps / total_apps * 100) if total_apps > 0 else 0, 1)
    
    # Profile completeness
    profile = StudentProfile.objects.filter(user=student_user).first()
    fields = ['phone', 'branch', 'cgpa', 'batch_year', 'skills', 'resume', 'linkedin_url']
    filled = sum(1 for f in fields if getattr(profile, f, None))
    completeness = round((filled / len(fields) * 100), 1)

    return {
        "total_applications": total_apps,
        "success_rate": success_rate,
        "profile_completeness": completeness,
        "interviews_scheduled": apps.filter(status='shortlisted').count(),
        "rejections": rejected_apps
    }

def get_company_analytics(company_user):
    drives = PlacementDrive.objects.filter(company=company_user)
    total_drives = drives.count()
    apps = Application.objects.filter(drive__company=company_user)
    total_applicants = apps.count()
    shortlisted = apps.filter(status='shortlisted').count()
    selected = apps.filter(status='selected').count()
    
    return {
        "total_drives": total_drives,
        "total_applicants": total_applicants,
        "shortlisted_candidates": shortlisted,
        "selected_candidates": selected,
        "selection_ratio": round((selected / total_applicants * 100) if total_applicants > 0 else 0, 1)
    }

def get_smart_matches(student_user):
    try:
        profile = student_user.studentprofile
    except:
        return []
        
    student_skills = set(profile.skills.values_list('name', flat=True))
    student_cgpa = profile.cgpa or 0.0
    student_branch = profile.branch

    matches = []
    drives = PlacementDrive.objects.filter(status='approved')
    for drive in drives:
        score = 0
        
        # CGPA Check (MANDATORY)
        if student_cgpa < drive.min_cgpa:
            continue
            
        # Branch Check
        if drive.eligible_branches and student_branch not in drive.eligible_branches:
            continue
            
        # Skills Match
        drive_skills = set(drive.required_skills.values_list('name', flat=True))
        if drive_skills:
            match_count = len(student_skills.intersection(drive_skills))
            score += (match_count / len(drive_skills)) * 100
        else:
            score += 100 # No skills required
            
        matches.append({
            "drive_id": drive.id,
            "job_title": drive.job_title,
            "company_name": drive.company.companyprofile.company_name,
            "match_score": round(score, 1)
        })
        
    matches.sort(key=lambda x: x['match_score'], reverse=True)
    return matches[:5]
