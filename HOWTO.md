# School ERP System - How-To Guide

Welcome to your professional School ERP system. This guide explains common workflows and how to get the most out of the application.

## 1. Initial Setup
1.  **Install Dependencies**: Run `pip install -r requirements.txt`.
2.  **Initialize Database**: Run `python seed.py`. This is essential to create the default admin account and set up the academic structure.

## 2. Managing the Academic Year
- **Creating Classes**: Go to **Classes** -> **Add New Class**. Use standard names like "JSS 1" or "SS 3".
- **Adding Subjects**: Within a class view, use **Add Subject** to define the curriculum for that class.
- **Enrolling Students**: Use **Add Student** in the class view. Provide full details including guardian contact information.

## 3. Recording Academic Performance
- **Creating Exams**: Go to **Manage Exams** in the class detail page. Define the weightage (e.g., 0.3 for Mid-Term, 0.7 for Finals).
- **Entering Marks**: Use the **Enter Marks** button next to an exam. This opens a bulk-entry sheet for the entire class.
- **Generating Results**: Click **Result** next to any student's name to view and print their progress report.

## 4. Administrative Tasks
- **Attendance**: Open the **Attendance** sheet from the class view daily to track student presence.
- **Fees**: Use the **Fees** dashboard to define costs for each class. Record payments under the student's fee details.
- **Promotion**: At the end of the year, use the **Promotion** tool in the class view to move eligible students to the next class grade.
- **Audit Logs**: Administrators can monitor system activity via **Settings** -> **View Audit Logs**.

## 5. Security Tips
- **Password Management**: Change the default admin password immediately in a production environment.
- **Roles**: Use the 'Admin' role for full system access and 'Teacher' for academic-focused tasks.

---
Developed by **Afedia Glory** & **Awani Caleb**.
