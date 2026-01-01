# Amrita Hospital HRMS - Backend System

A comprehensive Hospital Human Resource Management System built with Django.

## Features

### Role-Based Access Control
- **Admin**: Full system access, manage all departments, employees, and system settings
- **HR**: Manage recruitment, employees, leave requests, and job postings
- **Department Head**: Manage department staff and approve leave requests
- **Staff**: View personal information and submit leave requests

### Core Modules

#### 1. Authentication & User Management
- Custom user model with role-based permissions
- Secure login/logout functionality
- Profile management

#### 2. Department Management
- Manage hospital departments (Cardiology, Oncology, ICU, Neurosciences, etc.)
- Track department location, head, and capacity
- Department-wise analytics

#### 3. Staff Categories
- Medical Staff
- Nursing Staff
- Paramedical & Technical
- Admin & Support

#### 4. Employee Management
- Complete employee records with personal and professional details
- Employee ID, department assignment, and category
- Shift management (Morning, Afternoon, Night, General, Rotating)
- Salary and status tracking
- Emergency contact information

#### 5. Recruitment Management
- Job posting creation and management
- Public careers page for applicants
- Application tracking system
- Application review and interview scheduling
- Status tracking (Submitted, Under Review, Shortlisted, Interview Scheduled, Selected, Rejected)

#### 6. Leave Management
- Leave request submission by staff
- Multiple leave types (Sick, Casual, Earned, Maternity, Paternity, Emergency)
- Approval workflow for HR and Department Heads
- Leave history tracking

#### 7. Dashboards
- **Admin Dashboard**: System-wide analytics, department stats, employee overview
- **HR Dashboard**: Recruitment metrics, employee statistics, pending applications
- **Department Head Dashboard**: Department staff overview, pending leave requests
- **Staff Dashboard**: Personal information, leave history, and status

## Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip (Python package manager)

### Step 1: Create Virtual Environment
```bash
python -m venv venv
```

### Step 2: Activate Virtual Environment
**Windows:**
```bash
venv\Scripts\activate
```

**Linux/Mac:**
```bash
source venv/bin/activate
```

### Step 3: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 4: Run Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### Step 5: Create Superuser (Admin)
```bash
python manage.py createsuperuser
```
Follow the prompts to create an admin account.

### Step 6: Create Media Directory
```bash
mkdir media
mkdir media\resumes
```

### Step 7: Run Development Server
```bash
python manage.py runserver
```

The application will be available at: `http://127.0.0.1:8000/`

## Initial Setup

### 1. Access Admin Panel
Visit `http://127.0.0.1:8000/admin/` and login with your superuser credentials.

### 2. Create Departments
Add hospital departments through the admin panel or the web interface:
- Cardiology
- Oncology
- ICU
- Neurosciences
- Emergency Medicine
- General Surgery
- Pediatrics
- etc.

### 3. Create Users
Create users with different roles:
- Admin users for system management
- HR users for recruitment and employee management
- Department Head users for department oversight
- Staff users for regular employees

### 4. Create Employees
Link users to employee profiles with complete information.

## Project Structure

```
amrita_hrms/
│
├── manage.py                      # Django management script
│
├── amrita_hrms/                   # Main project configuration
│   ├── __init__.py
│   ├── settings.py                # Project settings
│   ├── urls.py                    # Root URL configuration
│   ├── asgi.py                    # ASGI configuration
│   └── wsgi.py                    # WSGI configuration
│
├── hospital_hr/                   # Main application
│   ├── __init__.py
│   ├── admin.py                   # Admin panel configurations
│   ├── apps.py                    # App configuration
│   ├── models.py                  # Database models
│   ├── forms.py                   # Form definitions
│   ├── views.py                   # View logic
│   ├── urls.py                    # App URL routing
│   ├── signals.py                 # Database signals
│   ├── decorators.py              # Role-based access decorators
│   └── migrations/                # Database migrations
│
├── media/                         # Uploaded files
│   └── resumes/                   # Applicant resumes
│
├── requirements.txt               # Python dependencies
└── .gitignore                     # Git ignore file
```

## Database Models

### User
- Custom user model extending Django's AbstractUser
- Fields: username, email, first_name, last_name, role, phone, employee_id, profile_picture

### Department
- Fields: name, code, location, head, description, phone, email, total_beds, is_active

### Employee
- Fields: user, employee_id, department, category, designation, shift, date_of_birth, date_of_joining, qualification, specialization, experience_years, salary, emergency_contact_*, address, status

### Job
- Fields: title, department, category, job_type, vacancies, description, requirements, responsibilities, min_experience, min_qualification, salary_min, salary_max, status, posted_by, posted_date, closing_date

### Application
- Fields: job, applicant_name, email, phone, date_of_birth, qualification, specialization, experience_years, current_employer, current_designation, resume, cover_letter, status, interview_date, interview_notes, reviewed_by

### LeaveRequest
- Fields: employee, leave_type, start_date, end_date, total_days, reason, status, approved_by, approval_date, rejection_reason

## API Endpoints

### Public Routes
- `/` - Landing page
- `/login/` - User login
- `/careers/` - Public job listings
- `/careers/<id>/` - Job details
- `/careers/<id>/apply/` - Job application form

### Authenticated Routes
- `/dashboard/` - Role-based dashboard
- `/departments/` - Department management
- `/employees/` - Employee management
- `/jobs/` - Job management (HR/Admin)
- `/applications/` - Application tracking (HR/Admin)
- `/leave-requests/` - Leave request management

## Security Features

- Role-based access control using custom decorators
- Password hashing with Django's built-in authentication
- CSRF protection enabled
- SQL injection protection through Django ORM
- XSS protection through template auto-escaping

## Future Enhancements

- AI-powered resume screening
- Advanced analytics and reporting
- Email notifications for applications and leave requests
- Calendar integration for interviews and shifts
- Performance evaluation module
- Payroll integration
- Attendance tracking system
- Training and certification management

## Technologies Used

- **Backend Framework**: Django 4.2+
- **Database**: SQLite (default) - can be changed to PostgreSQL/MySQL
- **Authentication**: Django Authentication System
- **File Storage**: Django File Storage (for resumes and documents)
- **Time Zone**: Asia/Kolkata (Indian Standard Time)

## Support

For issues or questions, please refer to the Django documentation at https://docs.djangoproject.com/

## License

This project is built for Amrita Hospital HRMS system.
