# 📘 User Documentation & Manuals

Welcome to the User Manual directory for the **Campus Placement Portal**. This document provides detailed, step-by-step user manuals, admin guides, an FAQ bank, and troubleshooting playbooks.

---

## 1. Student User Manual

As a student, the platform acts as your virtual command center to discover jobs, manage applications, and review performance metrics.

### Step 1: Login & Setup Profile
1. Navigate to the login screen and enter your credentials.
2. If this is your first time logging in, click **Edit Profile** in the top navigation panel.
3. Fill out your details: contact phone number, academic branch, current CGPA, batch year, resume PDF file, and preferred hiring locations.
4. Input your skills to allow the **Smart Match Recommendation Engine** to suggest highly compatible roles.
5. **⚙️ Expose Profile (Developer API Keys):** If you are building a custom website or portfolio integration:
   * Scroll down the profile page to the **🔑 Developer API Keys** card.
   * Provide a name (e.g., *"My Portfolio Widget"*) and click **Generate**.
   * Copy the raw secret token string (`pp_live_...`) immediately as it is only displayed once.
   * View live usage logs, last-used timestamps, and revoke keys at any time to block integrations.

### Step 2: Exploring Drives & Applying
1. Access the **Placement Dashboard**. Under **Available Drives**, you'll see hiring events currently open.
2. Use the search input to filter drives by role, company name, or minimum package keywords in real-time.
3. Review job eligibility (e.g., minimum CGPA, eligible branches, deadline).
4. Click **Apply Now** on the drive. Confirm the application in the warning prompt. The platform will automatically transmit your digital resume and student profile immediately.

### Step 3: Tracking Applications & Analytics
1. The **My Applications** pane displays all submitted opportunities.
2. Use the **Sort Applications** dropdown to prioritize applications by *Selected First*, *Shortlisted First*, or *Applied First*.
3. Click on the **Analytics** button to view:
   * **Success Rate:** Calculated based on successful selections vs. total submissions.
   * **Profile Completeness Index:** Highlights fields you need to fill.
   * **Skill Gaps:** Suggests specific skills requested in rejected applications.

---

## 2. Recruiter / Company User Manual

Recruiter profiles are configured to build drives, manage applicant pipelines, and review selection funnels.

### Step 1: Registering & Profiles
1. Create a company account at `/signup/company/`.
2. All new recruiters require manual review and verification from the campus administrator before they can open hiring drives.
3. Complete your profile, including legal company name, HR contacts, and website links.
4. **⚙️ ATS Integration (Developer API Keys):** If you want to automatically download candidates or sync drives with your external applicant tracking system:
   * Navigate to the **🔑 Developer API Keys** section on the right side of your profile editor.
   * Enter an identifier name (e.g., *"Workday Integration"*) and generate a secure key.
   * Use this key in headers (`X-API-Key`) when syncing candidate pipelines.

### Step 2: Publishing Hiring Drives
1. Click **Create Hiring Drive** from the company portal.
2. Input target job titles, eligibility requirements (e.g. minimum CGPA, branches), location parameters, CTC packages (in Lakhs per annum - LPA), and application deadlines.
3. List required skill tags to assist matching algorithms.

### Step 3: Candidate Selection & Funnels
1. Access the drive listing page to review the full table of applicant students.
2. Move candidates through pipelines:
   * Click **Shortlist** to schedule interviews.
   * Click **Select** to finalize placements.
   * Click **Reject** to dismiss candidates from active status.
3. Visit the **Analytics** dashboard to examine hiring statistics, average applicants per drive, and the candidate pipeline funnel.

---

## 3. Administrator Portal Guide

The campus administrator governs system resources, ticket resolutions, and verified participants.

### Step 1: User Verification
1. Access the **Admin Dashboard** stats row:
   * **Total Students:** Click this card to launch a detailed pop-up list displaying students, branches, and CGPAs.
   * **Total Companies:** Click this card to open a modal of registered companies and verify their HR contact details.
2. Scroll to the **Pending Registrations** block. Review company requests and click **Approve Recruiter** to enable platform access.

### Step 2: Moderating Placement Drives
1. Scroll to the **Pending Drives** section.
2. Review job description details, CTC ranges, and eligibility criteria.
3. Click **Approve Drive** to publish the opportunity to the student dashboard, or reject it if details are incomplete.

### Step 3: Resolving Help Tickets
1. Scroll to the **Support Queries** panel.
2. Review student or recruiter issues.
3. Enter replies and click **Resolve Support Query**. An instant notification will be delivered to the target user.

---

## 4. Platform FAQs

#### Q: How are JWT access tokens renewed?
A: Access tokens expire after 15 minutes. The JavaScript engine (`AppUI`) securely handles silent token renewals behind the scenes by querying the `/api/token/refresh/` route using your 7-day refresh token.

#### Q: What is a Developer API Key and how do I use it?
A: It is a persistent access credential allowing external developer systems (like a personal portfolio, recruiter ATS, or campus statistics board) to securely fetch data from the placement portal. To authenticate, include the header `X-API-Key: <your_key>` in your HTTP request. You can create and revoke keys at any time via your profile settings.

#### Q: How is the Selection Ratio calculated?
A: It is calculated as: `(Selected Candidates / Total Drive Applicants) * 100`.

#### Q: Can I update my CGPA once I've submitted applications?
A: Yes, student profile CGPAs are dynamic. However, individual placement drives will evaluate your eligibility based on the current CGPA registered in the database.

---

## 5. Troubleshooting Playbook

### Problem 1: Theme switches look laggy or flicker
* **Cause:** Browser layout recalculation (reflow) caused by heavy style overrides or blocking scripts in the body header.
* **Resolution:** Ensure the flicker-free script inside `<head>` runs immediately before body layout blocks. [enhancements.css](file:///d:/placement_portal/static/css/enhancements.css) is pre-configured with explicit property transitions (`will-change: transform`) to keep operations hardware-accelerated.

### Problem 2: SQLite database is locked
* **Cause:** Concurrent read/write threads attempting database edits during testing.
* **Resolution:** Terminate running server instances, verify there are no orphaned background Python worker processes, and run:
  ```powershell
  python manage.py runserver
  ```

### Problem 3: "Invalid credentials" error during login
* **Cause:** User has not been approved yet, or incorrect credentials.
* **Resolution:** Ensure the company account has been approved by the admin. Verify password defaults (`123` for seeded mock records).
