import os
import django
import random
from datetime import timedelta
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "placement_portal.settings")
django.setup()

from users.models import CustomUser, StudentProfile, CompanyProfile, Skill, Education, Project
from drives.models import PlacementDrive
from applications.models import Application
from dashboard.models import Notification

def create_dummy_resume():
    # Make sure media directory exists
    os.makedirs("media/resumes", exist_ok=True)
    resume_path = "media/resumes/dummy_resume.pdf"
    if not os.path.exists(resume_path):
        with open(resume_path, "w") as f:
            f.write("DUMMY PDF CONTENT: Aarav Sharma's Resume. SDE Career Objective, Skillsets, and Education Background.")
    return "resumes/dummy_resume.pdf"

def populate():
    print("Starting rich database population...")
    
    # 1. Clean existing records (avoiding admin superuser)
    print("Purging existing dynamic records...")
    Application.objects.all().delete()
    PlacementDrive.objects.all().delete()
    Project.objects.all().delete()
    Education.objects.all().delete()
    CustomUser.objects.filter(is_superuser=False).delete()
    Skill.objects.all().delete()
    Notification.objects.all().delete()
    print("Dynamic records purged successfully.")

    # Create admin if it doesn't exist
    if not CustomUser.objects.filter(username="admin").exists():
        CustomUser.objects.create_superuser("admin", "admin@placement.com", "admin123")
        print("Created admin user.")

    # 2. Populate Skills Pool
    skills_pool = [
        ("Python", "Tech"),
        ("Java", "Tech"),
        ("C++", "Tech"),
        ("JavaScript", "Tech"),
        ("React", "Tech"),
        ("Django", "Tech"),
        ("SQL", "Tech"),
        ("AWS", "Tech"),
        ("Docker", "Tech"),
        ("Machine Learning", "Tech"),
        ("TensorFlow", "Tech"),
        ("HTML/CSS", "Tech"),
        ("Figma", "Design"),
        ("Product Management", "Business"),
        ("Communication", "Soft Skills")
    ]
    skill_objects = {}
    for name, category in skills_pool:
        skill, _ = Skill.objects.get_or_create(name=name, defaults={"category": category})
        skill_objects[name] = skill
    print(f"Created {len(skill_objects)} skill tags.")

    # 3. Create Companies (12 Total)
    companies_data = [
        ("Google", "Google LLC", True, "California, USA", "10,000+ employees", "Software / IT", 1998, 4.8),
        ("Microsoft", "Microsoft Corporation", True, "Redmond, USA", "10,000+ employees", "Software / IT", 1975, 4.7),
        ("Amazon", "Amazon.com Inc", True, "Seattle, USA", "10,000+ employees", "E-Commerce", 1994, 4.5),
        ("Meta", "Meta Platforms Inc", True, "California, USA", "10,000+ employees", "Social Media / AI", 2004, 4.4),
        ("Nvidia", "Nvidia Corporation", True, "California, USA", "5,000-10,000 employees", "Hardware / AI", 1993, 4.9),
        ("Adobe", "Adobe Systems Inc", True, "San Jose, USA", "10,000+ employees", "SaaS / Design", 1982, 4.6),
        ("Stripe", "Stripe Inc", True, "San Francisco, USA", "1,000-5,000 employees", "FinTech", 2010, 4.5),
        ("Razorpay", "Razorpay Software", True, "Bengaluru, India", "1,000-5,000 employees", "FinTech", 2014, 4.3),
        ("Swiggy", "Swiggy Bundl Technologies", True, "Bengaluru, India", "5,000-10,000 employees", "On-Demand Delivery", 2014, 4.2),
        ("Netflix", "Netflix Inc", False, "Los Gatos, USA", "5,000-10,000 employees", "Streaming / SaaS", 1997, 4.7),
        ("Oracle", "Oracle Corporation", False, "Austin, USA", "10,000+ employees", "Database / Enterprise", 1977, 4.1),
        ("Zomato", "Zomato Limited", False, "Gurugram, India", "5,000-10,000 employees", "FoodTech", 2008, 4.0),
    ]

    company_users = []
    print("Creating company profiles...")
    for username, full_name, is_approved, hq, size, industry, founded, rating in companies_data:
        user = CustomUser.objects.create(
            username=username,
            email=f"hr@{username.lower()}.com",
            role="company",
            is_approved=is_approved
        )
        user.set_password("123")
        user.save()
        
        profile = CompanyProfile.objects.get(user=user)
        profile.company_name = full_name
        profile.hr_contact = f"+91 {random.randint(7000000000, 9999999999)}"
        profile.website = f"https://www.{username.lower()}.com"
        profile.description = f"Leading brand in the world of {industry}. Driven by innovation and user experience."
        profile.company_size = size
        profile.industry_type = industry
        profile.headquarters = hq
        profile.founded_year = founded
        profile.rating = rating
        profile.save()
        
        if is_approved:
            company_users.append(user)

    print(f"Created 12 company profiles (9 approved, 3 unapproved).")

    # 4. Create Placement Drives for Approved Companies (1 to 4 drives each)
    role_options = [
        {
            "title": "Software Engineer Intern",
            "description": "Join our Core SDE team working on building scalable microservices and robust API platforms. You will collaborate directly with senior engineering staff.",
            "ctc": 12.00,
            "job_type": "internship",
            "work_mode": "remote",
            "min_cgpa": 7.0,
            "eligible_branches": ["Computer Science", "Information Technology"],
            "selection_stages": ["Online Assessment", "Technical Interview Round 1", "Technical Interview Round 2", "HR Round"],
            "skills": ["Python", "Django", "JavaScript", "SQL"]
        },
        {
            "title": "Machine Learning Engineer",
            "description": "Seeking an ML Engineer to design, deploy, and scale predictive intelligence models. Experience with TensorFlow or PyTorch and data processing pipeline optimization is highly valued.",
            "ctc": 28.00,
            "job_type": "fulltime",
            "work_mode": "hybrid",
            "min_cgpa": 8.0,
            "eligible_branches": ["Computer Science", "Information Technology", "Electronics"],
            "selection_stages": ["ML Coding Test", "Research Paper Presentation", "Architecture Round", "Final HR"],
            "skills": ["Python", "Machine Learning", "TensorFlow", "SQL"]
        },
        {
            "title": "Cloud SRE Associate",
            "description": "Ensure the highest availability, latency, performance, and efficiency of our massive cloud infrastructure. You will optimize Kubernetes deployments.",
            "ctc": 16.50,
            "job_type": "fulltime",
            "work_mode": "onsite",
            "min_cgpa": 7.5,
            "eligible_branches": ["Computer Science", "Information Technology", "Electrical Engineering"],
            "selection_stages": ["Linux & Network Quiz", "Infrastructure Hands-on Test", "HR Round"],
            "skills": ["AWS", "Docker", "Python", "Communication"]
        },
        {
            "title": "UI/UX Researcher & Designer",
            "description": "Own the customer journey. You will map user flows, conduct user interviews, build beautiful wireframes, and design high-fidelity components using Figma.",
            "ctc": 10.00,
            "job_type": "internship",
            "work_mode": "remote",
            "min_cgpa": 6.5,
            "eligible_branches": ["Computer Science", "Information Technology", "Electronics", "Mechanical Engineering"],
            "selection_stages": ["Portfolio Review", "Interactive Design Challenge", "HR Round"],
            "skills": ["Figma", "HTML/CSS", "Communication"]
        },
        {
            "title": "Hardware Verification Engineer",
            "description": "Work at the cutting edge of physical silicon. Verify performance parameters of low-power chip architectures using SystemVerilog or C++ test suites.",
            "ctc": 22.00,
            "job_type": "fulltime",
            "work_mode": "onsite",
            "min_cgpa": 8.2,
            "eligible_branches": ["Electronics", "Electrical Engineering"],
            "selection_stages": ["Hardware Architecture Test", "Technical Panel Interview", "HR Round"],
            "skills": ["C++", "Python", "Communication"]
        }
    ]

    all_drives = []
    print("Creating placement drives...")
    for company_user in company_users:
        # Determine number of drives for this company (1 to 4)
        num_drives = random.randint(1, 4)
        selected_roles = random.sample(role_options, num_drives)
        
        for role in selected_roles:
            drive = PlacementDrive.objects.create(
                company=company_user,
                job_title=role["title"],
                job_description=role["description"],
                eligibility_criteria=f"Required CGPA: {role['min_cgpa']}+. Eligible branches: {', '.join(role['eligible_branches'])}.",
                application_deadline=timezone.localdate() + timedelta(days=random.randint(15, 60)),
                ctc=role["ctc"],
                salary_min=role["ctc"] * 0.8,
                salary_max=role["ctc"] * 1.2,
                location=random.choice(["Bengaluru", "Pune", "Hyderabad", "Remote", "Gurugram"]),
                job_type=role["job_type"],
                work_mode=role["work_mode"],
                openings=random.randint(3, 20),
                min_cgpa=role["min_cgpa"],
                eligible_branches=role["eligible_branches"],
                selection_stages=role["selection_stages"],
                status="approved"
            )
            # Add M2M Skills
            skills_to_add = [skill_objects[s] for s in role["skills"] if s in skill_objects]
            drive.required_skills.set(skills_to_add)
            all_drives.append(drive)

    print(f"Created {len(all_drives)} placement drives across the approved companies.")

    # 5. Create Students (36 Students with human names)
    student_names = [
        "Aarav", "Ananya", "Kabir", "Saanvi", "Ishaan", "Divya", "Vivaan", "Diya", "Karan", "Meera",
        "Rohan", "Neha", "Rahul", "Priya", "Vikram", "Anya", "Aditya", "Tara", "Samar", "Kavya",
        "Arjun", "Aditi", "Sahil", "Shruti", "Tarun", "Kunal", "Amit", "Varun", "Nidhi", "Gaurav",
        "Siddharth", "Pooja", "Aman", "Riya", "Nikhil", "Sneha"
    ]

    resume_rel_path = create_dummy_resume()
    branches = ["Computer Science", "Information Technology", "Electronics", "Electrical Engineering", "Mechanical Engineering"]
    locations = ["Bengaluru, Pune", "Remote, Hyderabad", "Mumbai, Bengaluru", "Noida, Gurgaon", "Remote, Pune"]
    
    project_ideas = [
        ("E-Commerce Web Application", "Developed a robust full-stack online marketplace with integrated payment gateway, product reviews, and inventory tracking using React, Django Rest Framework, and PostgreSQL.", ["Python", "Django", "React", "SQL"]),
        ("Autonomous Warehouse Drone", "Built a pathfinding and collision avoidance navigation algorithm for automated warehouse drones using Python and A* search optimization.", ["Python", "C++", "Machine Learning"]),
        ("Portfolio Website & Blog", "Designed a responsive glassmorphic personal resume and blogging platform utilizing HTML/CSS, Vanilla JS, and optimized performance.", ["JavaScript", "HTML/CSS", "Figma"]),
        ("AI Image Generator", "Built an end-to-end web app using Django and OpenAI APIs that generates user-prompted custom digital artworks.", ["Python", "Django", "Machine Learning", "Figma"]),
        ("DevOps Deployment Pipeline", "Configured a full CI/CD deployment pipeline for a containerized multi-tier microservice app utilizing Docker, GitHub Actions, and AWS.", ["AWS", "Docker", "SQL"])
    ]

    student_users = []
    print("Creating student profiles...")
    for idx, name in enumerate(student_names):
        # Create user account
        user = CustomUser.objects.create(
            username=name,
            email=f"{name.lower()}@example.com",
            role="student"
        )
        user.set_password("123")
        user.save()
        student_users.append(user)
        
        # Populate student profile details
        profile = StudentProfile.objects.get(user=user)
        profile.phone = f"+91 {random.randint(7000000000, 9999999999)}"
        profile.resume = resume_rel_path
        profile.branch = random.choice(branches)
        profile.cgpa = round(random.uniform(6.5, 9.8), 2)
        profile.batch_year = 2022
        profile.department = f"School of {profile.branch}"
        profile.graduation_year = 2026
        profile.linkedin_url = f"https://linkedin.com/in/{name.lower()}"
        profile.github_url = f"https://github.com/{name.lower()}"
        profile.tenth_marks = round(random.uniform(80.0, 99.0), 2)
        profile.twelfth_marks = round(random.uniform(75.0, 98.0), 2)
        profile.expected_salary = round(random.uniform(6.0, 32.0), 2)
        profile.preferred_locations = random.choice(locations)
        profile.previous_internships = f"Completed a 2-month summer internship at a rising tech firm as an SDE Intern. Contributed to core features."
        profile.save()
        
        # Set dynamic skills pool (3-6 random skills)
        num_skills = random.randint(3, 6)
        chosen_skill_names = random.sample(list(skill_objects.keys()), num_skills)
        chosen_skills = [skill_objects[s] for s in chosen_skill_names]
        profile.skills.set(chosen_skills)

        # 5.1 Create Education History
        Education.objects.create(
            student=profile,
            degree="High School (10th)",
            institution="State Secondary Public School",
            year_of_passing=2020,
            percentage=profile.tenth_marks
        )
        Education.objects.create(
            student=profile,
            degree="Senior Secondary (12th)",
            institution="DAV Higher Secondary School",
            year_of_passing=2022,
            percentage=profile.twelfth_marks
        )
        Education.objects.create(
            student=profile,
            degree="Bachelor of Technology",
            institution="National Institute of Technology",
            year_of_passing=2026,
            percentage=round(profile.cgpa * 9.5, 2)
        )

        # 5.2 Create Projects (1 to 2 projects)
        num_projects = random.randint(1, 2)
        selected_projects = random.sample(project_ideas, num_projects)
        for p_title, p_desc, p_skills in selected_projects:
            project = Project.objects.create(
                student=profile,
                title=p_title,
                description=p_desc,
                link=f"https://github.com/{name.lower()}/{p_title.lower().replace(' ', '-')}",
                start_date=timezone.localdate() - timedelta(days=120),
                end_date=timezone.localdate() - timedelta(days=60)
            )
            p_skills_objs = [skill_objects[s] for s in p_skills if s in skill_objects]
            project.technologies.set(p_skills_objs)

    print(f"Created {len(student_users)} detailed student profiles (education, projects, resume).")

    # 6. Apply Students to Drives (1 to 10 students per drive)
    print("Spawning applications...")
    statuses = ["applied", "shortlisted", "selected", "rejected"]
    weights = [0.35, 0.35, 0.15, 0.15]
    
    applications_count = 0
    for drive in all_drives:
        # Determine number of applicants for this specific drive
        num_applicants = random.randint(1, 10)
        potential_applicants = []
        
        # Select eligible students (who meet branch criteria and CGPA cutoff)
        for user in student_users:
            profile = user.studentprofile
            # Check branch
            if drive.eligible_branches and profile.branch not in drive.eligible_branches:
                continue
            # Check CGPA
            if profile.cgpa < drive.min_cgpa:
                continue
            potential_applicants.append(user)
            
        if not potential_applicants:
            # Fallback: ignore constraints if zero match to guarantee applicants
            potential_applicants = student_users
            
        selected_applicants = random.sample(potential_applicants, min(num_applicants, len(potential_applicants)))
        
        for student in selected_applicants:
            chosen_status = random.choices(statuses, weights=weights)[0]
            
            # Setup metadata based on status
            round_name = ""
            notes = ""
            feedback = ""
            
            if chosen_status == "applied":
                round_name = drive.selection_stages[0] if drive.selection_stages else "Online Screening"
                notes = "Your application has been received. recruiters are reviewing your profile."
            elif chosen_status == "shortlisted":
                round_idx = random.randint(1, len(drive.selection_stages) - 2) if len(drive.selection_stages) > 2 else 0
                round_name = drive.selection_stages[round_idx] if drive.selection_stages else "Technical Interview"
                notes = f"Congratulations! You are shortlisted for {round_name}."
            elif chosen_status == "selected":
                round_name = "Finalized"
                notes = "Congratulations! You have been selected for this position."
                feedback = "Exceptional performance across technical coding and core design rounds."
                
                # Update student's placement status to Placed
                profile = StudentProfile.objects.get(user=student)
                profile.placement_status = "Placed"
                profile.save()
            elif chosen_status == "rejected":
                round_idx = random.randint(0, len(drive.selection_stages) - 1) if drive.selection_stages else 0
                round_name = drive.selection_stages[round_idx] if drive.selection_stages else "Technical Round"
                notes = "Thank you for participating. We will not be moving forward with your application."
                feedback = "Strong skills, but missed out on optimal performance in the algorithmic design challenge."
                
            Application.objects.create(
                student=student,
                drive=drive,
                status=chosen_status,
                current_round=round_name,
                company_notes=notes,
                company_feedback=feedback,
                interview_date=timezone.now() + timedelta(days=random.randint(1, 10)) if chosen_status == "shortlisted" else None
            )
            applications_count += 1
            
            # Generate dummy notification
            if chosen_status != "applied":
                Notification.objects.create(
                    user=student,
                    message=f"Update: Your application status for {drive.job_title} at {drive.company.companyprofile.company_name} is now '{chosen_status.upper()}'."
                )

    print(f"Successfully generated {applications_count} mock applications with historical pipelines.")
    print("Database is fully populated!")
    print("Passwords for ALL users (students/companies): '123'")

if __name__ == "__main__":
    populate()
