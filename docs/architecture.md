# Architectural Overview

The School ERP system is built using a professional **Multi-Tenant (SaaS)** Flask architecture, following industry best practices for scalability and data isolation.

## Core Architectural Concepts

### 1. Multi-Tenancy (SaaS)
The application is designed to host multiple schools independently. Each school is a separate "tenant" in the database.
- **Data Isolation**: Almost all entities (`User`, `Class`, `Student`, etc.) are linked to a `School` via a `school_id`.
- **Subdomain Routing**: The application identifies the tenant based on the request's subdomain. For example, `lagos-heritage.schoolerp.com` maps to the "Lagos Heritage" tenant.
- **Shared Infrastructure**: All tenants share the same codebase and database infrastructure, allowing for easier maintenance and updates.

### 2. Academic Sessions (Year-Based Logic)
Recognizing that academic records are cyclical, the system uses a `Session` model.
- **Dynamic Context**: Data like classes, exams, and attendance are tied to a specific academic session (e.g., "2024/2025").
- **Current Session**: Each school has an active session. Users see data for the current session by default but can switch context when necessary.

### 3. Application Factory & Blueprints
- **Modular Design**: divided into specialized modules (`auth`, `classes`, `student_portal`, etc.) using Flask Blueprints.
- **Context Injection**: `g.school` and `g.current_session` are automatically injected into every request context to ensure queries are strictly scoped to the current tenant.

### 4. Hierarchical RBAC (Role-Based Access Control)
The system implements a deep hierarchy:
- **Principal/Admin**: Full oversight.
- **Form Teacher**: Management of a specific subclass.
- **Subject Teacher**: Subject-specific marks management.
- **Student**: Access to personal records.

## Technology Stack
- **Backend**: Python 3.12, Flask 3.1
- **ORM**: Flask-SQLAlchemy (with PRAGMA foreign_keys for SQLite)
- **Frontend**: Jinja2, Bootstrap 5, Chart.js
- **Testing**: Pytest-Flask
