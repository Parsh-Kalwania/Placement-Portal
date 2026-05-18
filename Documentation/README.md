# 📚 Campus Placement Portal Documentation Hub

Welcome to the central documentation depository for the **Campus Placement Portal**! 

This repository hosts a state-of-the-art campus recruitment management system built with **Django**, **Django REST Framework (DRF)**, and **SimpleJWT Stateless Authentication**. It features high-end glassmorphic dark/light UI interfaces, compositor-accelerated animations, and robust real-time analytics.

---

## 📂 Documentation Directory Map

We have structured the documentation into targeted directories to assist developers, platform administrators, and end-users:

### 1. [🛠️ Technical & Developer Guides](file:///d:/placement_portal/Documentation/TECHNICAL_DOCS.md)
*For software engineers, system admins, and open-source contributors.*
* **Architecture Overview:** Decoupled frontend/backend, client tokens storage, and theme configurations.
* **Database Schema Specifications:** Relational entity schemas, table models, and field types.
* **Local Workspace Setup:** Commands to configure, seed, and launch servers.
* **Production Deployment Guide:** Nginx setups, WSGI server sockets, and environmental configurations.

### 2. [📐 High-Level Design (HLD) Document](file:///d:/placement_portal/Documentation/HIGH_LEVEL_DESIGN.md)
*For system architects, project managers, and lead developers.*
* **Architectural Layers:** Layered interaction diagram showing Presentation, Gateway, Service, and Data divisions.
* **Component Responsibilities:** Primary duties of core subsystems (Authentication, Drives, Applications, Recommendations).
* **Data Flow Workflows:** Detailed request sequence diagrams mapping authenticated REST fetch operations.

### 3. [📐 Low-Level Design (LLD) Document](file:///d:/placement_portal/Documentation/LOW_LEVEL_DESIGN.md)
*For software engineers, database admins, and code-level contributors.*
* **UML Class Diagram:** Detailed class diagrams showing database models, field types, and Viewset controls.
* **Database Models Breakdown:** Concrete descriptions of CustomUser, StudentProfile, PlacementDrive, and Application fields.
* **API Controllers & Middleware:** Specific DRF View classes, method signatures, and custom authentication layers.

### 4. [🔌 REST API Endpoints Directory](file:///d:/placement_portal/Documentation/API_ENDPOINTS.md)
*Complete, comprehensive list of all backend REST endpoints, allowed HTTP methods, required query parameters, request bodies, permissions, and status codes.*

### 5. [📘 User Guides & Manuals](file:///d:/placement_portal/Documentation/USER_DOCS.md)
*For students, recruiters, and platform administrators.*
* **Student Manual:** Profile creation, smart job matches, filters, applications tracking, and analytics dashboards.
* **Company Manual:** Verifications, drive creation, pipeline management, and selection metrics.
* **Admin Manual:** Pending registrations reviews, drive approvals, and support ticket resolutions.
* **FAQ Sheet:** Common queries regarding platform features, credentials, and selection metrics.
* **Troubleshooting Playbook:** Real-world resolutions to SQLite locking, transition lag, and credentials.

---

## 🎯 Highlighted Platform Features

1. **Ultra-Premium UI:** Modern dark/light mode toggle with zero-flicker head initialization, glassmorphic card layouts, and hardware-accelerated left sidebar navigation.
2. **Stateless JWT Tokens Auth:** Employs a secure 15-minute access token lifespan combined with a silent 7-day auto-refresh cycle to eliminate credentials re-entry.
3. **Interactive Admin Metrics Directory:** Interactive dashboard stats tiles allowing superusers to view lists of students, companies, drives, and applications in detail cards via modals.
4. **Smart Match Algorithms:** High-fidelity profile-to-job matching score calculations utilizing student CGPA, skills gap analysis, and location preferences.
5. **Real-time Analytics:** Advanced student and recruiter analytics engines powered by native aggregate queries in Django.
