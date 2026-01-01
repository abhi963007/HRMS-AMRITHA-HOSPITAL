"""
Script to create Employee profiles for existing users
Run with: python setup_employee_profiles.py
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amrita_hrms.settings')
import sys
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
django.setup()

from hospital_hr.models import User, Employee, Department
from datetime import date

print("\n" + "="*70)
print("CREATING EMPLOYEE PROFILES FOR EXISTING USERS")
print("="*70 + "\n")

# Get or create a default department
default_dept, created = Department.objects.get_or_create(
    code='ADMIN',
    defaults={
        'name': 'Administration',
        'location': 'main_building',
        'description': 'Administrative department',
        'is_active': True
    }
)
if created:
    print(f"Created default department: {default_dept.name}")
else:
    print(f"Using existing department: {default_dept.name}")

# Create Employee profiles for users who don't have one
users_without_profile = []
for user in User.objects.all():
    try:
        emp = user.employee_profile
        print(f"✓ {user.username} already has employee profile: {emp.employee_id}")
    except Employee.DoesNotExist:
        users_without_profile.append(user)
        print(f"✗ {user.username} needs employee profile")

print(f"\n{len(users_without_profile)} users need employee profiles\n")

for user in users_without_profile:
    # Generate employee ID
    emp_id = f"EMP{user.id:04d}"
    
    # Determine category based on role
    if user.role in ['admin', 'hr']:
        category = 'admin_support'
        designation = 'HR Manager' if user.role == 'hr' else 'System Administrator'
    elif user.role == 'dept_head':
        category = 'medical'
        designation = 'Department Head'
    else:
        category = 'nursing'
        designation = 'Staff Nurse'
    
    # Create the Employee record
    employee = Employee.objects.create(
        user=user,
        employee_id=emp_id,
        department=default_dept,
        category=category,
        designation=designation,
        shift='general',
        date_of_joining=date.today(),
        salary=50000,
        status='active'
    )
    
    # Update user's employee_id field too
    user.employee_id = emp_id
    user.save()
    
    print(f"✓ Created employee profile for {user.username}: {emp_id} ({designation})")

print("\n" + "="*70)
print("DONE! All users now have employee profiles.")
print("="*70 + "\n")

# Show final status
print("Final User & Employee Status:")
print("-" * 70)
for user in User.objects.all():
    try:
        emp = user.employee_profile
        print(f"{user.username:15} | Role: {user.get_role_display():15} | Emp ID: {emp.employee_id}")
    except Employee.DoesNotExist:
        print(f"{user.username:15} | Role: {user.get_role_display():15} | NO PROFILE")
