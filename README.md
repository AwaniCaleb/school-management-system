# 🎓 Professional School ERP System (FYP Edition)

A modular, professional School ERP application built with Flask and SQLAlchemy. Designed as a Final Year Project for Computer Science students.

---

## ✨ Features

- **Modular Architecture**: Uses Flask Blueprints for clean code separation.
- **ORM Integration**: Powered by SQLAlchemy for secure and efficient database management.
- **Dynamic Dashboard**: Interactive analytics powered by Chart.js and RESTful APIs.
- **Full School Cycle**:
  - Class & Student Management
  - Bulk Marks Entry & Individual Result Cards
  - Attendance Tracking
  - Fee Structure & Payment History
- **Professional UI**: Responsive design with a sidebar layout built on Bootstrap 5.
- **Testing Suite**: Comprehensive unit tests using Pytest.
- **Documentation**: Detailed ER diagrams, architectural overviews, and user manuals.
- **Security & Logging**: Audit logs for user actions and role-based access control.

---

## 🧭 Quick Start

### 1. Installation
```bash
pip install -r requirements.txt
```

### 2. Database Setup (MANDATORY)
Initialize and seed the database with sample data. This creates the required tables and default accounts.
```bash
python seed.py
```

### 3. Run the App
```bash
python run.py
```
Open http://127.0.0.1:5000 in your browser.

---

## 🔑 Default Credentials

- **Admin**: `admin` / `admin123`
- **Teacher**: `teacher` / `teacher123`

---

## 📂 Project Structure
- `app/`: Main application package.
- `docs/`: Technical and user documentation.
- `tests/`: Automated test suite.
- `run.py`: Application entry point.
- `seed.py`: Database initialization script.

---

## 🧪 Running Tests
```bash
export PYTHONPATH=$PYTHONPATH:.
python -m pytest
```

---

## 👩‍💻 Documentation
For more details, see the `docs/` folder:
- [Architectural Overview](docs/architecture.md)
- [Database Schema](docs/database.md)
- [User Manual](docs/user_manual.md)

---

Made with 💜 as a CS Final Year Project.
