# Placement Portal Application

## Overview

The **Placement Portal Application** is a role-based web system built using **Django** and **Django REST Framework** to manage campus recruitment activities between institutes, companies, and students.

This system enables:

- 🎓 **Students** to register, apply for placement drives, and track application status  
- 🏢 **Companies** to create placement drives and manage applicants  
- 🛠 **Admin** to approve companies, approve drives, and manage users  

The project follows a **RESTful API architecture** with **JWT authentication** and **role-based access control (RBAC)**.

---

## Tech Stack

### Backend
- **Python**
- **Django**
- **Django REST Framework**
- **SimpleJWT (JWT Authentication)**
- **SQLite**

### Frontend
- **HTML**
- **Bootstrap**
- **Vanilla JavaScript (Fetch API)**

### Database
- **SQLite** (created programmatically using Django ORM)

---

## Core Features

### Authentication
- JWT-based login system
- Role-based access control
- Token-protected API endpoints

### Student Features
- Self-registration
- Edit profile (phone, resume link)
- View approved placement drives
- Apply for drives
- Track application status
- View placement history

### Company Features
- Registration (admin approval required)
- Create, edit, delete placement drives
- View applicants per drive
- Update application status:
  - Applied
  - Shortlisted
  - Selected
  - Rejected
- View full student profiles

### Admin Features
- Approve or reject companies
- Approve or reject drives
- Blacklist users
- Monitor overall placement activity

---

## Project Architecture

The project follows a modular Django structure:

- `users/` → Custom user model, authentication, profiles, permissions  
- `drives/` → Placement drive management  
- `applications/` → Student application handling  
- `placement_portal/` → Project configuration and routing  

### API vs Template Separation

- `/api/` → Returns **JSON responses**
- `/student/`, `/company/` → Render HTML templates  
- Frontend consumes APIs using `fetch()`

---

## Database Design

### 1. CustomUser
- `username`
- `role` (student/company)
- `is_approved`
- `is_blacklisted`

### 2. StudentProfile
- `user` (OneToOne with CustomUser)
- `full_name`
- `phone`
- `resume` (URLField)

### 3. CompanyProfile
- `user` (OneToOne with CustomUser)
- `company_name`
- `website`
- `hr_contact`

### 4. PlacementDrive
- `company` (ForeignKey)
- `job_title`
- `job_description`
- `eligibility_criteria`
- `application_deadline`
- `status`

### 5. Application
- `student` (ForeignKey)
- `drive` (ForeignKey)
- `status`
- **Unique constraint on (`student`, `drive`)** to prevent duplicate applications

---

## API Endpoints

### Authentication

```bash
POST /api/token/
POST /api/token/refresh/
```

### Registration

```bash
POST /api/register/student/
POST /api/register/company/
```

### Student APIs

```bash
GET   /api/student/dashboard/
GET   /api/student/profile/
PATCH /api/student/profile/
```

### Company APIs

```bash
GET   /api/company/dashboard/
GET   /api/company/student/<id>/
POST  /api/drives/
PATCH /api/drives/<id>/
```

### Application APIs

```bash
POST  /api/applications/
PATCH /api/applications/<id>/
```

### Drive APIs

```bash
GET /api/drives/
```

Supports filtering & search:

```bash
/api/drives/?status=approved
/api/drives/?search=developer
```

---

## Installation Guide

### 1. Clone Repository

```bash
git clone https://github.com/your-username/placement-portal.git
cd placement-portal
```

### 2. Create Virtual Environment

```bash
python -m venv venv
```

Activate:

**Windows**
```bash
venv\Scripts\activate
```

**Mac/Linux**
```bash
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Apply Migrations

```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Create Superuser

```bash
python manage.py createsuperuser
```

### 6. Run Server

```bash
python manage.py runserver
```

Visit:

```
http://127.0.0.1:8000/
```

---

## Authentication Flow

1. User logs in using `/api/token/`
2. Backend returns:
   - `access token`
   - `refresh token`
3. Access token is stored in browser `localStorage`
4. All protected requests include:

```http
Authorization: Bearer <access_token>
```

Backend validates JWT before processing requests.

---

## Design Principles Used

- RESTful API design
- Role-Based Access Control (RBAC)
- JWT-based stateless authentication
- Modular Django architecture
- Separation of frontend and backend logic
- Database-level integrity constraints

---

## Future Improvements

- Token auto-refresh handling
- Resume file upload support
- Email notifications
- Placement analytics dashboard
- Pagination for large datasets
- Deployment with PostgreSQL and Docker

---

## Author

**Parsh**  
