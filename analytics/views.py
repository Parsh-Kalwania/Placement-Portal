from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from django.db.models import Avg, Count, Max, Min, Q
from django.utils import timezone
from datetime import timedelta

from users.models import CustomUser, StudentProfile
from drives.models import PlacementDrive
from applications.models import Application


class StudentAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'student':
            raise PermissionDenied("Only students can access this.")

        apps = Application.objects.filter(student=user)
        total = apps.count()
        selected = apps.filter(status='selected').count()
        rejected = apps.filter(status='rejected').count()
        shortlisted = apps.filter(status='shortlisted').count()
        pending = apps.filter(status='applied').count()

        success_rate = round((selected / total * 100), 1) if total > 0 else 0

        # Profile completeness
        profile = StudentProfile.objects.filter(user=user).first()
        completeness_fields = {
            'Phone': bool(profile and profile.phone),
            'Branch': bool(profile and profile.branch),
            'CGPA': bool(profile and profile.cgpa),
            'Batch Year': bool(profile and profile.batch_year),
            'Resume': bool(profile and profile.resume),
            'LinkedIn': bool(profile and profile.linkedin_url),
            'GitHub': bool(profile and profile.github_url),
            'Skills': bool(profile and profile.skills.exists()),
            '10th Marks': bool(profile and profile.tenth_marks),
            '12th Marks': bool(profile and profile.twelfth_marks),
        }
        filled = sum(completeness_fields.values())
        completeness = round((filled / len(completeness_fields)) * 100, 1)

        # CGPA comparison
        student_cgpa = profile.cgpa if profile else None
        avg_placed_cgpa = StudentProfile.objects.filter(
            user__in=Application.objects.filter(status='selected').values('student')
        ).aggregate(avg=Avg('cgpa'))['avg']

        # Application timeline (last 6 months buckets)
        timeline = []
        for i in range(5, -1, -1):
            month_start = (timezone.now() - timedelta(days=30 * (i + 1))).date()
            month_end = (timezone.now() - timedelta(days=30 * i)).date()
            count = apps.filter(applied_at__date__gte=month_start, applied_at__date__lte=month_end).count()
            timeline.append({
                "label": month_start.strftime("%b %Y"),
                "count": count
            })

        # Skill gap: required skills in drives the student DIDN'T get into
        student_skills = set(profile.skills.values_list('name', flat=True)) if profile else set()
        missed_drives = apps.filter(status='rejected').values_list('drive', flat=True)
        skill_gap = {}
        if missed_drives:
            for drive in PlacementDrive.objects.filter(id__in=missed_drives):
                for skill in drive.required_skills.all():
                    if skill.name not in student_skills:
                        skill_gap[skill.name] = skill_gap.get(skill.name, 0) + 1
        top_skill_gaps = sorted(skill_gap.items(), key=lambda x: x[1], reverse=True)[:5]

        # Interview tips based on history
        tips = []
        if rejected > 0 and selected == 0:
            tips.append("Practice common technical interview questions for your target roles.")
            tips.append("Consider working on projects to strengthen your portfolio.")
        if shortlisted > 0 and selected == 0:
            tips.append("You're getting shortlisted! Focus on acing the interview rounds.")
        if top_skill_gaps:
            tips.append(f"You're missing these skills that rejected drives required: {', '.join([s[0] for s in top_skill_gaps[:3]])}.")
        if not profile or not profile.resume:
            tips.append("Upload your resume — many companies filter candidates without one.")
        if completeness < 70:
            tips.append("Complete your profile to get more visibility with recruiters.")

        return Response({
            "total_applications": total,
            "selected": selected,
            "shortlisted": shortlisted,
            "rejected": rejected,
            "pending": pending,
            "success_rate": success_rate,
            "profile_completeness": completeness,
            "completeness_breakdown": completeness_fields,
            "student_cgpa": student_cgpa,
            "avg_placed_cgpa": round(avg_placed_cgpa, 2) if avg_placed_cgpa else None,
            "application_timeline": timeline,
            "skill_gaps": [{"skill": s[0], "missed": s[1]} for s in top_skill_gaps],
            "tips": tips,
        })


class CompanyAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'company':
            raise PermissionDenied("Only companies can access this.")

        drives = PlacementDrive.objects.filter(company=user)
        total_drives = drives.count()
        apps = Application.objects.filter(drive__company=user)
        total_applicants = apps.count()
        shortlisted = apps.filter(status='shortlisted').count()
        selected = apps.filter(status='selected').count()
        rejected = apps.filter(status='rejected').count()

        # Hiring funnel
        funnel = [
            {"stage": "Applied", "count": total_applicants},
            {"stage": "Shortlisted", "count": shortlisted},
            {"stage": "Selected", "count": selected},
        ]

        # Response rate (shortlisted + rejected out of total)
        responded = shortlisted + rejected + selected
        response_rate = round((responded / total_applicants * 100), 1) if total_applicants > 0 else 0

        # Popular skills demanded (from this company's drives)
        skill_demand = {}
        for drive in drives:
            for skill in drive.required_skills.all():
                skill_demand[skill.name] = skill_demand.get(skill.name, 0) + 1
        top_skills = sorted(skill_demand.items(), key=lambda x: x[1], reverse=True)[:8]

        # Average applicants per drive
        avg_applicants = round(total_applicants / total_drives, 1) if total_drives > 0 else 0

        # Drives with most applicants
        drive_stats = []
        for drive in drives:
            d_apps = apps.filter(drive=drive)
            drive_stats.append({
                "title": drive.job_title,
                "applicants": d_apps.count(),
                "selected": d_apps.filter(status='selected').count(),
            })
        drive_stats.sort(key=lambda x: x['applicants'], reverse=True)

        return Response({
            "total_drives": total_drives,
            "total_applicants": total_applicants,
            "shortlisted": shortlisted,
            "selected": selected,
            "rejected": rejected,
            "selection_ratio": round((selected / total_applicants * 100), 1) if total_applicants > 0 else 0,
            "response_rate": response_rate,
            "avg_applicants_per_drive": avg_applicants,
            "hiring_funnel": funnel,
            "top_skills_demanded": [{"skill": s[0], "count": s[1]} for s in top_skills],
            "drive_performance": drive_stats[:5],
        })


class AdminAnalyticsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        if not request.user.is_superuser:
            raise PermissionDenied("Only admin can access this.")

        PlacementDrive.close_expired()

        # Core counts
        total_students = CustomUser.objects.filter(role='student').count()
        total_companies = CustomUser.objects.filter(role='company').count()
        approved_companies = CustomUser.objects.filter(role='company', is_approved=True).count()
        total_drives = PlacementDrive.objects.count()
        approved_drives = PlacementDrive.objects.filter(status='approved').count()
        total_apps = Application.objects.count()

        # Placement rate
        placed_student_ids = Application.objects.filter(status='selected').values('student').distinct()
        placed_count = placed_student_ids.count()
        placement_rate = round((placed_count / total_students * 100), 1) if total_students > 0 else 0

        # Avg CGPA of placed students
        avg_placed_cgpa = StudentProfile.objects.filter(
            user__in=placed_student_ids
        ).aggregate(avg=Avg('cgpa'))['avg']

        # Avg salary of selected drives
        avg_salary = PlacementDrive.objects.filter(
            application__status='selected'
        ).aggregate(avg=Avg('ctc'))['avg']

        # Branch-wise placements
        branch_stats = {}
        for profile in StudentProfile.objects.filter(user__in=placed_student_ids).select_related('user'):
            b = profile.branch or 'Unknown'
            branch_stats[b] = branch_stats.get(b, 0) + 1
        branch_data = sorted(branch_stats.items(), key=lambda x: x[1], reverse=True)

        # Total branch-wise students
        branch_total = {}
        for profile in StudentProfile.objects.all():
            b = profile.branch or 'Unknown'
            branch_total[b] = branch_total.get(b, 0) + 1

        # Company-wise hires
        company_hires = {}
        for app in Application.objects.filter(status='selected').select_related('drive__company__companyprofile'):
            try:
                cname = app.drive.company.companyprofile.company_name
            except Exception:
                cname = app.drive.company.username
            company_hires[cname] = company_hires.get(cname, 0) + 1
        top_companies = sorted(company_hires.items(), key=lambda x: x[1], reverse=True)[:8]

        # Application status breakdown (funnel)
        app_funnel = [
            {"stage": "Applied", "count": Application.objects.filter(status='applied').count()},
            {"stage": "Shortlisted", "count": Application.objects.filter(status='shortlisted').count()},
            {"stage": "Selected", "count": Application.objects.filter(status='selected').count()},
            {"stage": "Rejected", "count": Application.objects.filter(status='rejected').count()},
        ]

        # Peak application period (by month, last 6 months)
        monthly_apps = []
        for i in range(5, -1, -1):
            month_start = (timezone.now() - timedelta(days=30 * (i + 1))).date()
            month_end = (timezone.now() - timedelta(days=30 * i)).date()
            count = Application.objects.filter(
                applied_at__date__gte=month_start,
                applied_at__date__lte=month_end
            ).count()
            monthly_apps.append({
                "label": month_start.strftime("%b %Y"),
                "count": count
            })

        # Most in-demand skills across all approved drives
        skill_demand = {}
        for drive in PlacementDrive.objects.filter(status='approved'):
            for skill in drive.required_skills.all():
                skill_demand[skill.name] = skill_demand.get(skill.name, 0) + 1
        top_skills = sorted(skill_demand.items(), key=lambda x: x[1], reverse=True)[:8]

        # Job type breakdown
        job_type_data = {}
        for drive in PlacementDrive.objects.all():
            jt = drive.get_job_type_display()
            job_type_data[jt] = job_type_data.get(jt, 0) + 1

        return Response({
            # Summary Cards
            "total_students": total_students,
            "placed_students": placed_count,
            "placement_rate": placement_rate,
            "total_companies": total_companies,
            "approved_companies": approved_companies,
            "total_drives": total_drives,
            "approved_drives": approved_drives,
            "total_applications": total_apps,
            "avg_placed_cgpa": round(avg_placed_cgpa, 2) if avg_placed_cgpa else None,
            "avg_salary_lpa": round(float(avg_salary), 2) if avg_salary else None,

            # Charts
            "branch_placements": [{"branch": b, "placed": c, "total": branch_total.get(b, 0)} for b, c in branch_data],
            "top_hiring_companies": [{"company": c, "hires": h} for c, h in top_companies],
            "application_funnel": app_funnel,
            "monthly_applications": monthly_apps,
            "top_skills_demanded": [{"skill": s[0], "count": s[1]} for s in top_skills],
            "job_type_breakdown": [{"type": t, "count": c} for t, c in job_type_data.items()],
        })


class SmartMatchView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if user.role != 'student':
            raise PermissionDenied("Only students can access smart matches.")

        try:
            profile = user.studentprofile
        except Exception:
            return Response({"matches": [], "message": "Complete your profile to get recommendations."})

        student_skills = set(profile.skills.values_list('name', flat=True))
        student_cgpa = profile.cgpa or 0.0
        student_branch = profile.branch or ''

        # Exclude already applied drives
        applied_drive_ids = Application.objects.filter(student=user).values_list('drive_id', flat=True)
        drives = PlacementDrive.objects.filter(status='approved').exclude(id__in=applied_drive_ids)

        matches = []
        for drive in drives:
            score = 0
            reasons = []
            warnings = []

            # CGPA check
            if student_cgpa < drive.min_cgpa:
                warnings.append(f"Requires {drive.min_cgpa} CGPA (you have {student_cgpa})")
                continue  # Hard filter: skip ineligible

            # Branch check
            if drive.eligible_branches and student_branch not in drive.eligible_branches:
                continue  # Hard filter

            # Skills match (0–60 pts)
            drive_skills = set(drive.required_skills.values_list('name', flat=True))
            if drive_skills:
                matched = student_skills.intersection(drive_skills)
                skill_score = (len(matched) / len(drive_skills)) * 60
                score += skill_score
                if matched:
                    reasons.append(f"You match {len(matched)}/{len(drive_skills)} required skills")
                missing = drive_skills - student_skills
                if missing:
                    warnings.append(f"Missing skills: {', '.join(list(missing)[:3])}")
            else:
                score += 60  # No skill requirement — full points
                reasons.append("No specific skills required")

            # CGPA bonus (0–20 pts)
            if drive.min_cgpa > 0:
                cgpa_bonus = min(20, ((student_cgpa - drive.min_cgpa) / drive.min_cgpa) * 20)
                score += max(0, cgpa_bonus)
                if student_cgpa >= drive.min_cgpa:
                    reasons.append(f"CGPA eligible ({student_cgpa} ≥ {drive.min_cgpa})")

            # Location preference (0–20 pts)
            preferred = [loc.strip().lower() for loc in (profile.preferred_locations or '').split(',') if loc.strip()]
            drive_location = (drive.location or '').lower()
            if preferred and drive_location:
                if any(pref in drive_location for pref in preferred):
                    score += 20
                    reasons.append("Matches your preferred location")

            try:
                company_name = drive.company.companyprofile.company_name
            except Exception:
                company_name = drive.company.username

            matches.append({
                "drive_id": drive.id,
                "job_title": drive.job_title,
                "company_name": company_name,
                "location": drive.location or "Not specified",
                "job_type": drive.get_job_type_display(),
                "ctc": str(drive.ctc) if drive.ctc else None,
                "deadline": str(drive.application_deadline),
                "match_score": round(min(score, 100), 1),
                "reasons": reasons,
                "warnings": warnings,
            })

        matches.sort(key=lambda x: x['match_score'], reverse=True)
        return Response({
            "matches": matches[:10],
            "total_eligible": len(matches),
        })
