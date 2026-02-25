# User Manual

## 1. Getting Started as a Tenant
This platform is a SaaS application. Each school operates independently.

### Domain Access
- In production, your school will have its own subdomain: `your-school.erp-platform.com`.
- For development, the system identifies the first available school if no subdomain is provided.

### Default Login
| Role | Username | Password |
|------|----------|----------|
| Admin | `admin` | `admin123` |

## 2. Academic Sessions
The system is session-aware. At the start of a new academic year:
1.  Go to **Settings**.
2.  Add a new **Session** (e.g., 2025/2026).
3.  Click **Set Current** to make it the active session for your school.

## 3. Class Management (List View)
Classes are displayed in a consolidated list for easier navigation in large schools.
- **Assign Form Teacher**: Use the **Edit** button on a class to assign a teacher responsible for the entire class.
- **Assign Subject Teacher**: Use the **Edit** button on a subject to assign a teacher for that specific course.

## 4. Student Portals
Students can log in using their **Roll Number** (case-insensitive) and the default password `student123`.
- They can view their **Academic Progress** for the current and past sessions.
- They can monitor their **Outstanding Balance** for school fees.

## 5. Teacher Roles
- **Form Teachers**: Have full visibility into their assigned class, including attendance and all subject results.
- **Subject Teachers**: When they enter the **Marks Entry** sheet, they only have permission to edit scores for the subjects they teach.

## 6. Audit Logs
Administrators and Principals can monitor all sensitive actions (Logins, Mark changes, Student updates) via the **Audit Logs** in the Settings panel.
