# 🔌 REST API Endpoints Directory

This document contains a comprehensive, highly detailed listing of **all REST API endpoints** implemented in the Campus Placement Portal, their allowed HTTP methods, required query parameters, body formats, permissions, and typical response shapes.

---

## 🔐 1. Authentication & Register APIs

### `POST /api/token/`
* **Description:** Authenticates user credentials and generates JWT access and refresh tokens.
* **Access:** Public (Anonymous)
* **Request Body:**
  ```json
  {
    "username": "arjun",
    "password": "123"
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "access": "eyJhbGciOiJIUzI1...",
    "refresh": "eyJhbGciOiJIUzI1..."
  }
  ```
* **Error Response (401 Unauthorized):** `{"detail": "No active account found with the given credentials"}`

### `POST /api/token/refresh/`
* **Description:** Generates a new short-lived JWT access token using a valid 7-day refresh token.
* **Access:** Public (Anonymous)
* **Request Body:**
  ```json
  {
    "refresh": "eyJhbGciOiJIUzI1..."
  }
  ```
* **Success Response (200 OK):**
  ```json
  {
    "access": "eyJhbGciOiJIUzI1..."
  }
  ```

### `POST /api/register/student/`
* **Description:** Registers a new student account.
* **Access:** Public
* **Request Body:**
  ```json
  {
    "username": "StudentName",
    "email": "student@college.edu",
    "password": "123"
  }
  ```
* **Success Response (201 Created):** `{"id": 34, "username": "StudentName", "role": "student"}`

### `POST /api/register/company/`
* **Description:** Registers a new recruiter/company account. Accounts are unapproved by default and require administrator verification.
* **Access:** Public
* **Request Body:**
  ```json
  {
    "username": "Google",
    "email": "recruiter@google.com",
    "password": "123"
  }
  ```
* **Success Response (201 Created):** `{"id": 41, "username": "Google", "role": "company"}`

### `GET /api/me/`
* **Description:** Retrieves information about the currently logged-in user.
* **Access:** Authenticated Users
* **Success Response (200 OK):**
  ```json
  {
    "id": 14,
    "username": "Aarav",
    "email": "aarav@example.com",
    "role": "student",
    "is_approved": true,
    "is_superuser": false
  }
  ```

---

## 💼 2. Placement Drives APIs

### `GET /api/drives/`
* **Description:** Fetches a list of all active placement drives open to students. Supports standard keyword search and filter modifications.
* **Access:** Authenticated (Any Role)
* **Parameters:**
  * `?search=Software` (Matches keywords in title or descriptions)
  * `?ordering=-ctc` (Sorts descending by package scale)
* **Success Response (200 OK):**
  ```json
  {
    "count": 12,
    "next": null,
    "previous": null,
    "results": [
      {
        "id": 4,
        "company": "Amazon",
        "job_title": "Software Development Engineer",
        "ctc": "32.00",
        "application_deadline": "2026-06-30T18:30:00Z",
        "status": "approved"
      }
    ]
  }
  ```

### `POST /api/drives/`
* **Description:** Publishes a new placement drive opportunity.
* **Access:** Approved Recruiters Only
* **Request Body:**
  ```json
  {
    "job_title": "Data Analyst Intern",
    "job_description": "We are seeking a junior analyst...",
    "min_cgpa": "7.50",
    "ctc": "12.00",
    "location": "Bangalore",
    "job_type": "internship",
    "openings": 5,
    "application_deadline": "2026-07-15T23:59:59Z",
    "required_skills": ["SQL", "Python", "Tableau"]
  }
  ```

### `PATCH /api/drives/<int:pk>/`
* **Description:** Updates specific details of an existing placement drive.
* **Access:** Drive Owner (Recruiter) or Admin

### `GET /api/admin/drives/pending/`
* **Description:** Lists all new placement drives awaiting administrator approval.
* **Access:** Admin (Superuser)
* **Success Response (200 OK):** Array of pending drives.

### `PATCH /api/admin/drives/<int:pk>/approve/`
* **Description:** Approves a pending placement drive, making it active and visible to eligible students.
* **Access:** Admin (Superuser)
* **Success Response (200 OK):** `{"status": "approved"}`

---

## 📝 3. Candidate Applications APIs

### `GET /api/applications/`
* **Description:** Lists student applications.
  * For **Students:** Lists their personal submitted applications.
  * For **Recruiters:** Lists applications submitted to their company's drives.
* **Access:** Authenticated (Any Role)
* **Success Response (200 OK):** Array of application records.

### `POST /api/applications/`
* **Description:** Submits a student's resume profile to an active job drive.
* **Access:** Authenticated Students
* **Request Body:** `{"drive": 8}`
* **Success Response (201 Created):**
  ```json
  {
    "id": 105,
    "student": "Aarav",
    "drive": 8,
    "status": "applied",
    "applied_at": "2026-05-18T16:00:00Z"
  }
  ```

### `PATCH /api/applications/<int:pk>/`
* **Description:** Updates the status or round details of a submitted application. Used to manage the candidate selection pipeline.
* **Access:** Drive Owner (Recruiter) or Admin
* **Request Body:**
  ```json
  {
    "status": "shortlisted",
    "current_round": "Technical Interview 1",
    "company_notes": "Highly proficient in system architectures."
  }
  ```
* **Success Response (200 OK):** Updated application object.

### `GET /api/student/placement-history/`
* **Description:** Retrieves all successfully finalized placements (`status='selected'`) for the logged-in student.
* **Access:** Student Role
* **Success Response (200 OK):**
  ```json
  {
    "total_placements": 1,
    "placements": [
      {
        "id": 12,
        "job_title": "Software Engineer",
        "company_name": "Microsoft",
        "ctc": "44.00"
      }
    ]
  }
  ```

---

## 🎓 4. Student & Recruiter Profiles APIs

### `GET /api/student/profile/`
* **Description:** Fetches the logged-in student's academic profile details.
* **Access:** Student Role

### `PUT /api/student/profile/`
* **Description:** Updates the student's academic metrics, resume attachment, and skill tags.
* **Access:** Student Role
* **Request Body (Multipart Form Data):**
  * `phone`: `"9988776655"`
  * `branch`: `"Computer Science"`
  * `cgpa`: `9.20`
  * `batch_year`: `2026`
  * `skills`: `["Python", "Django", "React"]`
  * `resume`: `[File Binary Upload]`

### `GET /api/company/profile/`
* **Description:** Fetches details of the recruiter's company profile.
* **Access:** Company Role

### `GET /api/company/student/<int:pk>/`
* **Description:** Allows an approved recruiter to view a student applicant's full academic profile and download their resume safely.
* **Access:** Approved Recruiters Only

---

## 📊 5. Analytics & Dashboard APIs

### `GET /api/student/dashboard/`
* **Description:** Retrieves real-time student workspace indicators (counts of active drives, application statuses, and shortlisted counts).
* **Access:** Student Role

### `GET /api/company/dashboard/stats/`
* **Description:** Retrieves real-time hiring metrics for recruiters (pending drives, shortlisted applicants, selection ratio).
* **Access:** Company Role

### `GET /api/admin/dashboard/`
* **Description:** Retrieves administrator workspace stats (student totals, verified recruiters counts, pending requests).
* **Access:** Admin (Superuser)

### `GET /api/admin/list-data/`
* **Description:** Safely lists platform model records in administrative lists, mapped inside modals on clicking dashboard metric cards.
* **Access:** Admin (Superuser)
* **Query Parameters:** `?type=students` | `?type=companies` | `?type=drives` | `?type=applications`
* **Success Response (200 OK):** List of corresponding metadata rows.

### `GET /api/student/analytics/`
* **Description:** Computes complex aggregate indicators for students, such as success ratios, profile completeness ratings, and skill gap metrics.
* **Access:** Student Role

### `GET /api/company/analytics/`
* **Description:** Calculates hiring funnel metrics, popular skill demands, and drive performance analytics for companies.
* **Access:** Company Role

### `GET /api/admin/analytics/`
* **Description:** Generates campus placement rates, branch placement distributions, average salaries (LPA), and hiring company metrics.
* **Access:** Admin (Superuser)

### `GET /api/student/smart-matches/`
* **Description:** Runs a matching algorithm comparing student profile parameters (skills, CGPA, branch eligibility) against active job postings, scoring them on a 0-100% match index.
* **Access:** Student Role

---

## 🔔 6. Support & System Notifications APIs

### `GET /api/notifications/`
* **Description:** Retrieves the latest 30 platform notifications for the logged-in user, along with the count of unread notifications.
* **Access:** Authenticated Users

### `POST /api/notifications/`
* **Description:** Marks all unread system notifications as read.
* **Access:** Authenticated Users
* **Success Response (200 OK):** `{"status": "success"}`

### `POST /api/support/`
* **Description:** Submits a support query/help ticket.
* **Access:** Authenticated Users
* **Request Body:** `{"subject": "Resume update issue", "message": "My resume does not upload properly..."}`
* **Success Response (201 Created):** `{"status": "success", "message": "Support request submitted successfully"}`

### `GET /api/support/history/`
* **Description:** Fetches all help tickets opened by the logged-in student or company user, along with replies from the administrator.
* **Access:** Authenticated Users

### `GET /api/admin/support/`
* **Description:** Lists platform support tickets for administration moderation.
* **Access:** Admin (Superuser)
* **Query Parameters:** `?status=unresolved` | `?status=resolved`

### `PATCH /api/admin/support/<int:pk>/resolve/`
* **Description:** Records an administrator's response to a help ticket and marks it as resolved. Sends an instant notification to the target user.
* **Access:** Admin (Superuser)
* **Request Body:** `{"reply": "We have updated the allowed file size for resume uploads to 5MB."}`
* **Success Response (200 OK):** `{"status": "success"}`

---

## 🔑 7. Developer API Keys APIs

Exposes endpoints allowing developers (students or companies) to manage their persistent credentials for server-to-server integrations.

### `GET /api/developer/keys/`
* **Description:** Retrieves all active API Keys owned by the logged-in developer.
* **Access:** Authenticated Users
* **Success Response (200 OK):**
  ```json
  [
    {
      "id": 1,
      "name": "Local Resume Analyzer",
      "key_preview": "pp_live_7c4f...4ae1",
      "created_at": "2026-05-18T16:10:00Z",
      "last_used": "2026-05-18T16:12:45Z"
    }
  ]
  ```

### `POST /api/developer/keys/`
* **Description:** Generates a brand-new persistent developer API Key.
* **Access:** Authenticated Users
* **Request Body:** `{"name": "Local Resume Analyzer"}`
* **Success Response (201 Created):**
  ```json
  {
    "message": "API Key generated successfully. Please copy it now as it will not be displayed again.",
    "id": 1,
    "name": "Local Resume Analyzer",
    "key": "pp_live_7c4f039d6e492bbfa14ae1938592d192",
    "created_at": "2026-05-18T16:10:00Z"
  }
  ```

### `DELETE /api/developer/keys/<int:pk>/`
* **Description:** Instantly revokes and deletes the target developer API Key, disabling any further integration access carrying this key.
* **Access:** Key Owner
* **Success Response (200 OK):** `{"message": "API Key revoked successfully."}`

