# Quick Setup Guide - Amrita Hospital HRMS

## Step-by-Step Installation

### 1. Create Virtual Environment
```bash
python -m venv venv
```

### 2. Activate Virtual Environment

**Windows (PowerShell):**
```powershell
venv\Scripts\activate
```

**Windows (CMD):**
```cmd
venv\Scripts\activate.bat
```

### 3. Install Dependencies
```bash
pip install -r requirements.txt
```

### 4. Create Database & Apply Migrations
```bash
python manage.py makemigrations
python manage.py migrate
```

### 5. Load Sample Data (Optional but Recommended)
```bash
python setup.py
```

This will create:
- Admin user (username: `admin`, password: `admin123`)
- HR user (username: `hr_manager`, password: `hr123`)
- 8 hospital departments

**OR** Create Superuser Manually:
```bash
python manage.py createsuperuser
```

### 6. Run Development Server
```bash
python manage.py runserver
```

### 7. Access the Application

- **Main Application**: http://127.0.0.1:8000/
- **Admin Panel**: http://127.0.0.1:8000/admin/
- **Careers Page**: http://127.0.0.1:8000/careers/

## Default Accounts (if using setup.py)

### Admin Account
- Username: `admin`
- Password: `admin123`
- Role: Administrator
- Access: Full system access

### HR Account
- Username: `hr_manager`
- Password: `hr123`
- Role: HR Manager
- Access: Employee & recruitment management

## Next Steps

1. **Login to Admin Panel** (http://127.0.0.1:8000/admin/)
   - Use admin credentials
   - Explore the data models

2. **Create Additional Users**
   - Create Department Heads
   - Create Staff users
   - Assign appropriate roles

3. **Add Employees**
   - Go to Employees section
   - Add employee records with all details
   - Link to user accounts

4. **Post Jobs**
   - Create job postings
   - Jobs will appear on the careers page
   - Accept applications

5. **Test Different Dashboards**
   - Login as different role users
   - Each role sees a customized dashboard

## Troubleshooting

### Port Already in Use
```bash
python manage.py runserver 8001
```

### Database Errors
Delete `db.sqlite3` and run migrations again:
```bash
del db.sqlite3
python manage.py makemigrations
python manage.py migrate
python setup.py
```

### Static Files Not Loading
```bash
python manage.py collectstatic
```

## Project Features

✅ Role-based authentication (Admin, HR, Dept Head, Staff)
✅ Department management
✅ Employee management with complete records
✅ Recruitment & job posting system
✅ Application tracking
✅ Leave management system
✅ Multiple dashboards based on user role
✅ Analytics and reporting

## Tech Stack

- Django 4.2+
- SQLite (Development)
- Python 3.8+
- Bootstrap (Ready for frontend)

## Need Help?

Refer to `README.md` for detailed documentation.
