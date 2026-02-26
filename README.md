# 🎓 Professional School ERP System (FYP)

A comprehensive, modular School Enterprise Resource Planning (ERP) application built with **Flask** and **SQLAlchemy**. This project was designed and developed as a **Computer Science Final Year Project** to meet professional standards of software engineering, security, and documentation.

---

## 👥 Authors
- **Afedia Glory**
- **Awani Caleb**

---

## ✨ Features

- **Modular Architecture**: Built using Flask Blueprints and the Application Factory pattern for scalability and maintainability.
- **ORM Integration**: Powered by SQLAlchemy for secure and efficient database management.
- **Dynamic Dashboard**: Interactive system analytics with real-time charts (Chart.js) and RESTful API endpoints.
- **Nigerian Academic Context**: Pre-configured for Nigerian secondary school structures (JSS/SS).
- **Role-Based Portals**: Dedicated interfaces for Admin, Principal, Teachers, and Students.
- **Core Modules**:
  - **Class & Student Management**: Centralized student directory with detailed profiles.
  - **Academic Records**: Specialized marks entry (Subject-specific for teachers), weighted scoring, and automated result card generation.
  - **Attendance Tracking**: Daily attendance recording with an intuitive interface.
  - **Financial Management**: Fee structure definition and student payment history tracking.
  - **Security & Accountability**: Role-based access control (Admin/Teacher) and comprehensive System Audit Logs.
- **Professional UI**: Responsive, sidebar-based layout built on Bootstrap 5.
- **Exporting**: Download student lists and results in CSV format; printable result cards.

---

## 🧭 Quick Start

### 1. Prerequisites
- Python 3.10+
- Pip

### 2. Installation
```bash
pip install -r requirements.txt
```

### 3. Database Setup (MANDATORY)
Initialize and seed the database with professional Nigerian sample data:
```bash
python seed.py
```

### 4. Run the Application
```bash
python run.py
```
Access the system at: http://127.0.0.1:5000

---

## 🔑 Default Credentials

| Role    | Username  | Password   |
|---------|-----------|------------|
| Admin   | `admin`   | `admin123` |
| Teacher | `teacher` | `teacher123`|

---

## 📂 Project Structure
- `app/`: Core application package (models, routes, templates, static files).
- `docs/`: Technical and architectural documentation.
- `tests/`: Automated test suite for quality assurance.
- `run.py`: Entry point for starting the development server.
- `seed.py`: Professional data seeder script.

---

## 🧪 Testing & Quality
Run the automated test suite to verify system integrity:
```bash
export PYTHONPATH=$PYTHONPATH:.
python -m pytest
```

---

## 👩‍💻 Documentation
For in-depth details, refer to the `docs/` directory:
- [Architectural Overview](docs/architecture.md)
- [Database Schema (ER Diagram)](docs/database.md)
- [User Manual](docs/user_manual.md)

---

Copyright © 2025 Afedia Glory & Awani Caleb. All Rights Reserved.
