# Architectural Overview

The School ERP system is built using a modular Flask architecture, following industry best practices for scalability and maintainability.

## Design Patterns

### 1. Application Factory Pattern
Instead of a global `app` object, we use `create_app()` in `app/__init__.py`. This allows for multiple instances of the app (e.g., for testing) and cleaner configuration management.

### 2. Blueprints
The application logic is divided into specialized modules using Flask Blueprints:
- **Auth**: User session management and Audit Logging.
- **Main**: Dashboard and search functionality.
- **Classes**: Class, subject, and promotion management.
- **Students**: Student profile management with expanded fields.
- **Student Portal**: Dedicated read-only access for student accounts.
- **Exams**: Exam scheduling and bulk marks entry.
- **Fees**: Fee structure and payment tracking.
- **Attendance**: Daily attendance recording.
- **API**: JSON endpoints for frontend analytics.
- **Settings**: System-wide configuration and log viewing.

### 3. Object-Relational Mapping (ORM)
We use **Flask-SQLAlchemy** to interface with the SQLite database. This abstracts raw SQL queries into Python objects, improving security and code readability.

### 4. Granular Permissions & Roles
The system implements a sophisticated hierarchical permission model:
- **Admin**: Full system access, including technical configuration.
- **Principal**: High-level management, log viewing, and fee management.
- **Vice Principal**: Academic and student record management.
- **Form Teacher**: Full management rights for their specific assigned class (Attendance, Results verification).
- **Subject Teacher**: Edit access restricted only to the subjects they teach.
- **Student**: Read-only access to their own profile, results, and fee status.

## Technology Stack
- **Backend**: Python 3.12, Flask 3.1
- **Database**: SQLite (SQLAlchemy)
- **Frontend**: Jinja2, Bootstrap 5, Chart.js, FontAwesome
- **Testing**: Pytest
- **Production**: Gunicorn
