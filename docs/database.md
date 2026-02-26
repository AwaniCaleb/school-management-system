# Database Documentation

This project uses SQLite with SQLAlchemy ORM.

## ER Diagram (Mermaid)

```mermaid
erDiagram
    SCHOOL ||--o{ SESSION : owns
    SCHOOL ||--o{ USER : contains
    SCHOOL ||--o{ CLASS : has
    SCHOOL ||--o{ STUDENT : manages

    SESSION ||--o{ EXAM : scoped_to
    SESSION ||--o{ FEE_STRUCTURE : scoped_to
    SESSION ||--o{ ATTENDANCE_SESSION : scoped_to
    SESSION ||--o{ SUBJECT_TEACHER_ASSIGNMENT : defines

    USER ||--o{ CLASS : form_teacher_of
    USER ||--o{ SUBJECT_TEACHER_ASSIGNMENT : teaches
    USER ||--o| STUDENT : links_to

    CLASS ||--o{ STUDENT : contains
    CLASS ||--o{ EXAM : schedules
    CLASS ||--o{ ATTENDANCE_SESSION : tracks
    CLASS ||--o{ FEE_STRUCTURE : defines

    STUDENT ||--o{ MARK : receives
    STUDENT ||--o{ ATTENDANCE_RECORD : has
    STUDENT ||--o{ FEE_PAYMENT : makes

    SUBJECT ||--o{ MARK : recorded_in
    SUBJECT ||--o{ SUBJECT_TEACHER_ASSIGNMENT : assigned_to
    EXAM ||--o{ MARK : belongs_to

    ATTENDANCE_SESSION ||--o{ ATTENDANCE_RECORD : contains
    FEE_STRUCTURE ||--o{ FEE_PAYMENT : paid_for

    SCHOOL {
        int id
        string name
        string subdomain
        string logo_url
    }

    SESSION {
        int id
        int school_id
        string name
        bool is_current
    }

    USER {
        int id
        string username
        string password_hash
        string role
        string full_name
        string email
        string phone_number
        int student_id
    }

    CLASS {
        int id
        string class_name
        string section
        int form_teacher_id
    }

    STUDENT {
        int id
        string name
        string roll_no
        string gender
        string dob
        string blood_group
        string religion
        string state_of_origin
        string address
        string guardian_name
        string guardian_phone
        string contact_no
        string enrollment_date
        string status
        text medical_notes
        int class_id
    }

    SUBJECT {
        int id
        int school_id
        string subject_name
    }

    SUBJECT_TEACHER_ASSIGNMENT {
        int id
        int session_id
        int class_id
        int subject_id
        int teacher_id
    }

    EXAM {
        int id
        string name
        string exam_type
        float weight
        int class_id
    }

    MARK {
        int student_id
        int subject_id
        int exam_id
        float marks_obtained
    }

    ATTENDANCE_SESSION {
        int id
        int class_id
        string date
    }

    ATTENDANCE_RECORD {
        int id
        int session_id
        int student_id
        string status
    }

    FEE_STRUCTURE {
        int id
        int class_id
        string name
        float amount
        string due_date
    }

    FEE_PAYMENT {
        int id
        int student_id
        int fee_id
        float paid_amount
        string paid_on
        string mode
    }

    AUDIT_LOG {
        int id
        int user_id
        string action
        datetime timestamp
    }
```
