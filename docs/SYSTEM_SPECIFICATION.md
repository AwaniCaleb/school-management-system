# System Specification & Blueprint: Professional School ERP

## 1. Project Overview
**Project Title:** Professional School ERP (SaaS Architecture)
**Authors:** Afedia Glory & Awani Caleb
**Objective:** To provide a production-ready, multi-tenant school management system that streamlines academic, administrative, and financial operations for Nigerian secondary schools.

This document serves as the comprehensive "Brain" of the application. It outlines the current logic, architectural boundaries, and future roadmap to guide future development or remodeling efforts.

---

## 2. Core Architecture

### 2.1 Multi-Tenancy (SaaS)
The system uses a **Database-Level Multi-Tenancy** approach using a shared database with discriminator columns (`school_id`).
- **Data Isolation**: Every core entity (User, Student, Class, Subject, Fee, etc.) is linked to a `School`.
- **Context Filtering**: All queries are automatically filtered by `g.school.id` via the application context.
- **Academic Scoping**: Data is further segmented by `Session`. Users focus on the "Current Session" while retaining access to historical records.

### 2.2 Role-Based Access Control (RBAC)
| Role | Boundary & Permissions |
| :--- | :--- |
| **Admin** | Global system access. Manages users, schools, and audit logs. |
| **Principal** | Chief administrative officer for a specific school. Full access to school-specific settings, staff, and records. |
| **VP Admin** | Responsible for financial and administrative health. Manages fees and school-wide settings (Read-only). |
| **VP Academic** | Oversees academic integrity. Can manage subjects, classes, and override marks. |
| **HOD** | Head of Department. Can view and edit marks for all subjects assigned to their specific department. |
| **Teacher** | Scoped access. Can only view students they teach and enter marks for their assigned subjects. |
| **Student** | Read-only access to their own academic performance and financial status. |

---

## 3. Business Logic Details

### 3.1 Academic Grading (Nigerian Standard)
The system adopts a hybrid of internal continuous assessment and WAEC/NECO standards.
- **Scale (Internal)**:
  - **A (Excellent)**: 70 - 100
  - **B (Very Good)**: 60 - 69
  - **C (Good/Credit)**: 50 - 59
  - **D (Pass)**: 45 - 49
  - **E (Fair Pass)**: 40 - 44
  - **F (Fail)**: 0 - 39
- **Calculations**: Final scores are derived from weights (e.g., 30% CA, 70% Exam) defined at the `Exam` level.

### 3.2 Student Promotion Logic
Promotion is a critical "Gatekeeper" logic in the system:
1.  **Automated Eligibility**: A student is flagged as "Promotable" if they score a minimum grade of **'C' (50+)** in *all* subjects registered for the current session.
2.  **Manual Override**: The **Principal** or **VP Academic** can manually promote students who fall slightly short of the automated criteria (e.g., due to illness or special circumstances).
3.  **Process**: Upon promotion, the student is migrated to the target `Class` and their previous records are archived as "Session History."

### 3.3 Financial Logic
- **Fee Structures**: Fees are defined per Class and per Session.
- **Payment Lifecycle**: `Unpaid` -> `Partial` -> `Fully Paid`.
- **Balance Tracking**: Total Balance = (Sum of Fee Structure for Class) - (Sum of Payments).

---

## 4. Technical Specifications

### 4.1 Technology Stack
- **Framework**: Flask (Python) using Application Factory pattern.
- **Database**: SQLAlchemy (ORM) with support for SQLite/PostgreSQL.
- **Frontend**: Bootstrap 5 with custom "Soft UI" aesthetics and Chart.js for data visualization.
- **Deployment**: Configured for WSGI servers (Gunicorn) with a Heroku-ready Procfile.

### 4.2 Database Entity Relationships
- **School (1:N) Users**: A school has many staff and students.
- **Class (1:N) Students**: Students are enrolled in specific classes.
- **Subject (N:M) Classes**: Subjects are assigned to classes via `SubjectTeacherAssignment`, which also links a specific **Teacher** and **Session**.
- **Exam (1:N) Marks**: Marks are child records of an Exam, linked to both a Student and a Subject.

---

## 5. Future Roadmap (Road to V2)

### 5.1 Online Payment Integration
- **Implementation**: Integrate **Paystack** or **Flutterwave** API.
- **Workflow**: Student initiates payment in-portal -> Redirect to Gateway -> Callback updates `FeePayment` record -> Instant receipt generation.

### 5.2 Parent Portal
- **Logic**: Create a `Parent` model linked to one or more `Student` IDs.
- **View**: Real-time access to child’s attendance, results, and fee status.

### 5.3 Automated Notifications
- **Trigger**: Upon result publication or fee deadline.
- **Method**: Integration with **Twilio** (SMS) or **SendGrid** (Email).

---

## 6. Developer & AI Guidelines
*To any developer or AI assistant working on this repository:*
- **Simplicity First**: Maintain the Flask/Jinja2 stack for ease of hosting and modification in a school environment.
- **Consistency**: All new routes must follow the `@login_required` and `@require_role` patterns.
- **Multitenancy**: Never query an object without filtering by `school_id`.
- **Refinement**: If you identify a cleaner way to handle promotion logic or data visualization, propose it before implementation.

---
*End of Specification*
