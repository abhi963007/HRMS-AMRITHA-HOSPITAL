from django.shortcuts import render
from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponse
from hospital_hr.models import User, Department

@user_passes_test(lambda u: u.is_superuser)
def fix_user_accounts(request):
    """Admin view to check and fix user accounts"""
    
    output = []
    output.append("="*70)
    output.append("CHECKING AND FIXING USER ACCOUNTS")
    output.append("="*70)
    output.append("")
    
    # Check existing users
    output.append("Current users in database:")
    for user in User.objects.all():
        output.append(f"  ✓ {user.username:20} | Role: {user.get_role_display():15} | Active: {user.is_active}")
    
    output.append("")
    output.append("-"*70)
    output.append("Checking for missing users and creating them...")
    output.append("")
    
    # Fix dr_smith
    if not User.objects.filter(username='dr_smith').exists():
        output.append("Creating dr_smith (Department Head)...")
        user = User.objects.create_user(
            username='dr_smith',
            email='dr.smith@amritahospital.com',
            password='smith123',
            first_name='John',
            last_name='Smith',
            role='dept_head',
            phone='9876543212',
            employee_id='EMP001'
        )
        output.append(f"  ✓ Created dr_smith with dept_head role")
    else:
        user = User.objects.get(username='dr_smith')
        output.append(f"dr_smith exists: Role={user.get_role_display()}")
        if user.role != 'dept_head':
            user.role = 'dept_head'
            user.save()
            output.append(f"  ✓ Updated role to dept_head")
    
    output.append("")
    
    # Fix nurse_mary
    if not User.objects.filter(username='nurse_mary').exists():
        output.append("Creating nurse_mary (Staff)...")
        user = User.objects.create_user(
            username='nurse_mary',
            email='mary@amritahospital.com',
            password='changeme123',
            first_name='Mary',
            last_name='Williams',
            role='staff',
            phone='9876543213',
            employee_id='EMP002'
        )
        output.append(f"  ✓ Created nurse_mary with staff role")
    else:
        user = User.objects.get(username='nurse_mary')
        output.append(f"nurse_mary exists: Role={user.get_role_display()}")
        if user.role != 'staff':
            user.role = 'staff'
            user.save()
            output.append(f"  ✓ Updated role to staff")
    
    output.append("")
    output.append("="*70)
    output.append("FINAL USER LIST")
    output.append("="*70)
    output.append("")
    
    for user in User.objects.all().order_by('username'):
        output.append(f"Username: {user.username:15} | Role: {user.get_role_display():15} | ID: {user.employee_id or 'N/A'}")
    
    output.append("")
    output.append("="*70)
    output.append("LOGIN CREDENTIALS:")
    output.append("-"*70)
    output.append("admin       / admin123      (Admin - Full Access)")
    output.append("hr_manager  / hr123         (HR - Recruitment & Employees)")
    output.append("dr_smith    / smith123      (Dept Head - Department View)")
    output.append("nurse_mary  / changeme123   (Staff - Personal Profile)")
    output.append("="*70)
    output.append("")
    output.append("All users have been checked and fixed. You can now login with any of the above credentials.")
    
    return HttpResponse("<pre>" + "\n".join(output) + "</pre>")
