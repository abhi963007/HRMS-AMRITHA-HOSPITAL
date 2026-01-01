import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'amrita_hrms.settings')
django.setup()

from hospital_hr.models import User, Department


def create_sample_data():
    print("Creating sample data for Amrita Hospital HRMS...")
    
    print("\n1. Creating Admin User...")
    admin_user, created = User.objects.get_or_create(
        username='admin',
        defaults={
            'email': 'admin@amrita-hospital.com',
            'first_name': 'System',
            'last_name': 'Administrator',
            'role': 'admin',
            'is_staff': True,
            'is_superuser': True,
        }
    )
    if created:
        admin_user.set_password('admin123')
        admin_user.save()
        print("✓ Admin user created (username: admin, password: admin123)")
    else:
        print("✓ Admin user already exists")
    
    print("\n2. Creating HR User...")
    hr_user, created = User.objects.get_or_create(
        username='hr_manager',
        defaults={
            'email': 'hr@amrita-hospital.com',
            'first_name': 'HR',
            'last_name': 'Manager',
            'role': 'hr',
            'phone': '+91-9876543210',
        }
    )
    if created:
        hr_user.set_password('hr123')
        hr_user.save()
        print("✓ HR user created (username: hr_manager, password: hr123)")
    else:
        print("✓ HR user already exists")
    
    print("\n3. Creating Departments...")
    departments_data = [
        {'name': 'Cardiology', 'code': 'CARD', 'location': 'block_a', 'total_beds': 50},
        {'name': 'Oncology', 'code': 'ONCO', 'location': 'block_b', 'total_beds': 40},
        {'name': 'ICU', 'code': 'ICU', 'location': 'emergency_wing', 'total_beds': 30},
        {'name': 'Neurosciences', 'code': 'NEURO', 'location': 'block_c', 'total_beds': 35},
        {'name': 'Emergency Medicine', 'code': 'EMER', 'location': 'emergency_wing', 'total_beds': 25},
        {'name': 'General Surgery', 'code': 'GSURG', 'location': 'main_building', 'total_beds': 45},
        {'name': 'Pediatrics', 'code': 'PEDI', 'location': 'block_a', 'total_beds': 40},
        {'name': 'Orthopedics', 'code': 'ORTHO', 'location': 'block_b', 'total_beds': 35},
    ]
    
    for dept_data in departments_data:
        dept, created = Department.objects.get_or_create(
            code=dept_data['code'],
            defaults=dept_data
        )
        if created:
            print(f"✓ Created department: {dept.name}")
        else:
            print(f"✓ Department already exists: {dept.name}")
    
    print("\n" + "="*50)
    print("Setup completed successfully!")
    print("="*50)
    print("\nYou can now:")
    print("1. Run: python manage.py runserver")
    print("2. Access admin panel: http://127.0.0.1:8000/admin/")
    print("3. Login with:")
    print("   - Admin: username='admin', password='admin123'")
    print("   - HR: username='hr_manager', password='hr123'")
    print("\n" + "="*50)


if __name__ == '__main__':
    create_sample_data()
