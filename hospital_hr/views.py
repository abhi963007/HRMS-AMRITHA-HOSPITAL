from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from django.http import HttpResponse
import csv
from .models import User, Department, Employee, Job, Application, LeaveRequest, Attendance
from .forms import (
    UserLoginForm, UserRegistrationForm, DepartmentForm, EmployeeForm,
    JobForm, ApplicationForm, ApplicationReviewForm, LeaveRequestForm, LeaveApprovalForm,
    AttendanceForm, AttendanceFilterForm, AttendanceReportForm
)
from .decorators import (
    role_required, admin_required, hr_or_admin_required,
    dept_head_or_admin_required, staff_required
)


def landing_view(request):
    if request.user.is_authenticated:
        return redirect('hospital_hr:dashboard')
    
    departments = Department.objects.filter(is_active=True)[:6]
    open_jobs = Job.objects.filter(status='open')[:5]
    
    context = {
        'departments': departments,
        'open_jobs': open_jobs,
    }
    return render(request, 'hospital_hr/landing.html', context)


def login_view(request):
    if request.user.is_authenticated:
        return redirect('hospital_hr:dashboard')
    
    if request.method == 'POST':
        form = UserLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                # Clear any old messages before adding new one
                storage = messages.get_messages(request)
                storage.used = True
                messages.success(request, f'Welcome back, {user.get_full_name()}!')
                return redirect('hospital_hr:dashboard')
        else:
            # Clear old messages before showing error
            storage = messages.get_messages(request)
            storage.used = True
            messages.error(request, 'Invalid username or password.')
    else:
        form = UserLoginForm()
    
    return render(request, 'hospital_hr/login.html', {'form': form})


@login_required
def logout_view(request):
    logout(request)
    messages.info(request, 'You have been logged out successfully.')
    return redirect('hospital_hr:landing')


@login_required
def dashboard_view(request):
    user = request.user
    
    if user.role == 'admin':
        return admin_dashboard(request)
    elif user.role == 'hr':
        return hr_dashboard(request)
    elif user.role == 'dept_head':
        return dept_head_dashboard(request)
    else:
        return staff_dashboard(request)


def admin_dashboard(request):
    total_departments = Department.objects.filter(is_active=True).count()
    total_employees = Employee.objects.filter(status='active').count()
    total_jobs = Job.objects.filter(status='open').count()
    total_applications = Application.objects.filter(status='submitted').count()
    
    employees_by_category = Employee.objects.filter(status='active').values('category').annotate(
        count=Count('id')
    ).order_by('-count')
    
    employees_by_department = Employee.objects.filter(status='active').values(
        'department__name'
    ).annotate(count=Count('id')).order_by('-count')[:5]
    
    employees_on_leave = Employee.objects.filter(status='on_leave').count()
    
    recent_employees = Employee.objects.filter(status='active').select_related('user', 'department')[:5]
    pending_leaves = LeaveRequest.objects.filter(status='pending')[:5]
    recent_applications = Application.objects.filter(status='submitted').select_related('job')[:5]
    
    context = {
        'total_departments': total_departments,
        'total_employees': total_employees,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'employees_by_category': employees_by_category,
        'employees_by_department': employees_by_department,
        'employees_on_leave': employees_on_leave,
        'recent_employees': recent_employees,
        'pending_leaves': pending_leaves,
        'recent_applications': recent_applications,
    }
    return render(request, 'hospital_hr/dashboard_admin.html', context)


def hr_dashboard(request):
    total_employees = Employee.objects.filter(status='active').count()
    total_jobs = Job.objects.filter(status='open').count()
    total_applications = Application.objects.count()
    pending_applications = Application.objects.filter(status='submitted').count()
    
    employees_by_category = Employee.objects.filter(status='active').values('category').annotate(
        count=Count('id')
    )
    
    recent_applications = Application.objects.select_related('job').order_by('-applied_date')[:10]
    open_jobs = Job.objects.filter(status='open').select_related('department')[:5]
    pending_leaves = LeaveRequest.objects.filter(status='pending').select_related('employee__user')[:10]
    
    context = {
        'total_employees': total_employees,
        'total_jobs': total_jobs,
        'total_applications': total_applications,
        'pending_applications': pending_applications,
        'employees_by_category': employees_by_category,
        'recent_applications': recent_applications,
        'open_jobs': open_jobs,
        'pending_leaves': pending_leaves,
    }
    return render(request, 'hospital_hr/dashboard_hr.html', context)


def dept_head_dashboard(request):
    try:
        department = request.user.headed_department.first()
    except:
        department = None
    
    if department:
        dept_employees = Employee.objects.filter(department=department, status='active')
        total_dept_staff = dept_employees.count()
        on_duty = dept_employees.exclude(status='on_leave').count()
        on_leave = dept_employees.filter(status='on_leave').count()
        
        dept_employees_list = dept_employees.select_related('user')[:10]
        pending_leaves = LeaveRequest.objects.filter(
            employee__department=department,
            status='pending'
        ).select_related('employee__user')[:10]
    else:
        total_dept_staff = 0
        on_duty = 0
        on_leave = 0
        dept_employees_list = []
        pending_leaves = []
    
    context = {
        'department': department,
        'total_dept_staff': total_dept_staff,
        'on_duty': on_duty,
        'on_leave': on_leave,
        'dept_employees': dept_employees_list,
        'pending_leaves': pending_leaves,
    }
    return render(request, 'hospital_hr/dashboard_dept_head.html', context)


def staff_dashboard(request):
    try:
        employee = request.user.employee_profile
    except:
        employee = None
    
    if employee:
        # Get all leaves for counting
        all_leaves = LeaveRequest.objects.filter(employee=employee)
        approved_leaves = all_leaves.filter(status='approved').count()
        pending_leaves = all_leaves.filter(status='pending').count()
        rejected_leaves = all_leaves.filter(status='rejected').count()
        
        # Get recent leaves for display (slice at the end)
        my_leaves = all_leaves.order_by('-created_at')[:10]
    else:
        my_leaves = []
        approved_leaves = 0
        pending_leaves = 0
        rejected_leaves = 0
    
    context = {
        'employee': employee,
        'my_leaves': my_leaves,
        'approved_leaves': approved_leaves,
        'pending_leaves': pending_leaves,
        'rejected_leaves': rejected_leaves,
    }
    return render(request, 'hospital_hr/dashboard_staff.html', context)


@hr_or_admin_required
def department_list(request):
    departments = Department.objects.all().select_related('head')
    
    context = {
        'departments': departments,
    }
    return render(request, 'hospital_hr/department_list.html', context)


@hr_or_admin_required
def department_create(request):
    if request.method == 'POST':
        form = DepartmentForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department created successfully!')
            return redirect('hospital_hr:department_list')
    else:
        form = DepartmentForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'hospital_hr/department_form.html', context)


@hr_or_admin_required
def department_edit(request, pk):
    department = get_object_or_404(Department, pk=pk)
    
    if request.method == 'POST':
        form = DepartmentForm(request.POST, instance=department)
        if form.is_valid():
            form.save()
            messages.success(request, 'Department updated successfully!')
            return redirect('hospital_hr:department_list')
    else:
        form = DepartmentForm(instance=department)
    
    context = {
        'form': form,
        'action': 'Edit',
        'department': department,
    }
    return render(request, 'hospital_hr/department_form.html', context)


@admin_required
def department_delete(request, pk):
    department = get_object_or_404(Department, pk=pk)
    if request.method == 'POST':
        department.delete()
        messages.success(request, 'Department deleted successfully!')
        return redirect('hospital_hr:department_list')
    
    context = {
        'department': department,
    }
    return render(request, 'hospital_hr/department_confirm_delete.html', context)


@hr_or_admin_required
def employee_list(request):
    employees = Employee.objects.all().select_related('user', 'department')
    
    category = request.GET.get('category')
    department = request.GET.get('department')
    status = request.GET.get('status')
    search = request.GET.get('search')
    
    if category:
        employees = employees.filter(category=category)
    if department:
        employees = employees.filter(department_id=department)
    if status:
        employees = employees.filter(status=status)
    if search:
        employees = employees.filter(
            Q(employee_id__icontains=search) |
            Q(user__first_name__icontains=search) |
            Q(user__last_name__icontains=search) |
            Q(designation__icontains=search)
        )
    
    departments = Department.objects.filter(is_active=True)
    
    context = {
        'employees': employees,
        'departments': departments,
    }
    return render(request, 'hospital_hr/employee_list.html', context)


@hr_or_admin_required
def employee_create(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data['username'],
                email=form.cleaned_data['email'],
                first_name=form.cleaned_data['first_name'],
                last_name=form.cleaned_data['last_name'],
                password=form.cleaned_data.get('password', 'temppass123'),
                role='staff'
            )
            
            employee = form.save(commit=False)
            employee.user = user
            user.employee_id = employee.employee_id
            user.save()
            employee.save()
            
            messages.success(request, 'Employee created successfully!')
            return redirect('hospital_hr:employee_list')
    else:
        form = EmployeeForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'hospital_hr/employee_form.html', context)


@hr_or_admin_required
def employee_edit(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    
    if request.method == 'POST':
        form = EmployeeForm(request.POST, instance=employee, instance_user=employee.user)
        if form.is_valid():
            user = employee.user
            user.username = form.cleaned_data['username']
            user.email = form.cleaned_data['email']
            user.first_name = form.cleaned_data['first_name']
            user.last_name = form.cleaned_data['last_name']
            
            if form.cleaned_data.get('password'):
                user.set_password(form.cleaned_data['password'])
            
            user.save()
            
            employee = form.save(commit=False)
            user.employee_id = employee.employee_id
            user.save()
            employee.save()
            
            messages.success(request, 'Employee updated successfully!')
            return redirect('hospital_hr:employee_list')
    else:
        form = EmployeeForm(instance=employee, instance_user=employee.user)
    
    context = {
        'form': form,
        'action': 'Edit',
        'employee': employee,
    }
    return render(request, 'hospital_hr/employee_form.html', context)


@hr_or_admin_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    leave_requests = LeaveRequest.objects.filter(employee=employee).order_by('-created_at')[:10]
    
    context = {
        'employee': employee,
        'leave_requests': leave_requests,
    }
    return render(request, 'hospital_hr/employee_detail.html', context)


@admin_required
def employee_delete(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.method == 'POST':
        user = employee.user
        employee.delete()
        user.delete()
        messages.success(request, 'Employee deleted successfully!')
        return redirect('hospital_hr:employee_list')
    
    context = {
        'employee': employee,
    }
    return render(request, 'hospital_hr/employee_confirm_delete.html', context)


@hr_or_admin_required
def job_list(request):
    jobs = Job.objects.all().select_related('department', 'posted_by')
    
    status = request.GET.get('status')
    department = request.GET.get('department')
    category = request.GET.get('category')
    
    if status:
        jobs = jobs.filter(status=status)
    if department:
        jobs = jobs.filter(department_id=department)
    if category:
        jobs = jobs.filter(category=category)
    
    departments = Department.objects.filter(is_active=True)
    
    context = {
        'jobs': jobs,
        'departments': departments,
    }
    return render(request, 'hospital_hr/job_list.html', context)


@hr_or_admin_required
def job_create(request):
    if request.method == 'POST':
        form = JobForm(request.POST)
        if form.is_valid():
            job = form.save(commit=False)
            job.posted_by = request.user
            job.save()
            messages.success(request, 'Job posted successfully!')
            return redirect('hospital_hr:job_list')
    else:
        form = JobForm()
    
    context = {
        'form': form,
        'action': 'Create',
    }
    return render(request, 'hospital_hr/job_form.html', context)


@hr_or_admin_required
def job_edit(request, pk):
    job = get_object_or_404(Job, pk=pk)
    
    if request.method == 'POST':
        form = JobForm(request.POST, instance=job)
        if form.is_valid():
            form.save()
            messages.success(request, 'Job updated successfully!')
            return redirect('hospital_hr:job_list')
    else:
        form = JobForm(instance=job)
    
    context = {
        'form': form,
        'action': 'Edit',
        'job': job,
    }
    return render(request, 'hospital_hr/job_form.html', context)


@hr_or_admin_required
def job_detail(request, pk):
    job = get_object_or_404(Job, pk=pk)
    applications = Application.objects.filter(job=job).order_by('-applied_date')
    
    context = {
        'job': job,
        'applications': applications,
    }
    return render(request, 'hospital_hr/job_detail.html', context)


@admin_required
def job_delete(request, pk):
    job = get_object_or_404(Job, pk=pk)
    if request.method == 'POST':
        job.delete()
        messages.success(request, 'Job deleted successfully!')
        return redirect('hospital_hr:job_list')
    
    context = {
        'job': job,
    }
    return render(request, 'hospital_hr/job_confirm_delete.html', context)


def job_apply(request, pk):
    job = get_object_or_404(Job, pk=pk, status='open')
    
    if request.method == 'POST':
        form = ApplicationForm(request.POST, request.FILES)
        if form.is_valid():
            application = form.save(commit=False)
            application.job = job
            application.save()
            messages.success(request, 'Application submitted successfully!')
            return redirect('hospital_hr:job_public_detail', pk=job.pk)
    else:
        form = ApplicationForm()
    
    context = {
        'form': form,
        'job': job,
    }
    return render(request, 'hospital_hr/job_apply.html', context)


def job_public_list(request):
    jobs = Job.objects.filter(status='open').select_related('department')
    
    category = request.GET.get('category')
    department = request.GET.get('department')
    
    if category:
        jobs = jobs.filter(category=category)
    if department:
        jobs = jobs.filter(department_id=department)
    
    departments = Department.objects.filter(is_active=True)
    
    context = {
        'jobs': jobs,
        'departments': departments,
    }
    return render(request, 'hospital_hr/job_public_list.html', context)


def job_public_detail(request, pk):
    job = get_object_or_404(Job, pk=pk, status='open')
    
    context = {
        'job': job,
    }
    return render(request, 'hospital_hr/job_public_detail.html', context)


@hr_or_admin_required
def application_list(request):
    applications = Application.objects.all().select_related('job', 'reviewed_by')
    
    status = request.GET.get('status')
    job = request.GET.get('job')
    
    if status:
        applications = applications.filter(status=status)
    if job:
        applications = applications.filter(job_id=job)
    
    jobs = Job.objects.all()
    
    context = {
        'applications': applications,
        'jobs': jobs,
    }
    return render(request, 'hospital_hr/application_list.html', context)


@hr_or_admin_required
def application_detail(request, pk):
    application = get_object_or_404(Application, pk=pk)
    
    if request.method == 'POST':
        form = ApplicationReviewForm(request.POST, instance=application)
        if form.is_valid():
            app = form.save(commit=False)
            app.reviewed_by = request.user
            app.save()
            messages.success(request, 'Application updated successfully!')
            return redirect('hospital_hr:application_detail', pk=pk)
    else:
        form = ApplicationReviewForm(instance=application)
    
    context = {
        'application': application,
        'form': form,
    }
    return render(request, 'hospital_hr/application_detail.html', context)


@staff_required
def leave_request_create(request):
    try:
        employee = request.user.employee_profile
    except:
        messages.error(request, 'You must be an employee to request leave.')
        return redirect('hospital_hr:dashboard')
    
    if request.method == 'POST':
        form = LeaveRequestForm(request.POST)
        if form.is_valid():
            leave_request = form.save(commit=False)
            leave_request.employee = employee
            leave_request.save()
            messages.success(request, 'Leave request submitted successfully!')
            return redirect('hospital_hr:dashboard')
    else:
        form = LeaveRequestForm()
    
    context = {
        'form': form,
    }
    return render(request, 'hospital_hr/leave_request_form.html', context)


@hr_or_admin_required
def leave_request_list(request):
    leave_requests = LeaveRequest.objects.all().select_related('employee__user', 'approved_by')
    
    status = request.GET.get('status')
    department = request.GET.get('department')
    
    if status:
        leave_requests = leave_requests.filter(status=status)
    if department:
        leave_requests = leave_requests.filter(employee__department_id=department)
    
    departments = Department.objects.filter(is_active=True)
    
    context = {
        'leave_requests': leave_requests,
        'departments': departments,
    }
    return render(request, 'hospital_hr/leave_request_list.html', context)


@hr_or_admin_required
def leave_request_approve(request, pk):
    leave_request = get_object_or_404(LeaveRequest, pk=pk)
    
    if request.method == 'POST':
        form = LeaveApprovalForm(request.POST, instance=leave_request)
        if form.is_valid():
            leave = form.save(commit=False)
            leave.approved_by = request.user
            leave.approval_date = timezone.now()
            leave.save()
            
            if leave.status == 'approved':
                leave.employee.status = 'on_leave'
                leave.employee.save()
            
            messages.success(request, 'Leave request processed successfully!')
            return redirect('hospital_hr:leave_request_list')
    else:
        form = LeaveApprovalForm(instance=leave_request)
    
    context = {
        'form': form,
        'leave_request': leave_request,
    }
    return render(request, 'hospital_hr/leave_request_approve.html', context)


@login_required
def access_denied(request):
    return render(request, 'hospital_hr/access_denied.html')


# ============================================
# ATTENDANCE MANAGEMENT VIEWS
# ============================================

@login_required
@hr_or_admin_required
def attendance_dashboard(request):
    """HR/Admin attendance dashboard - mark and view attendance for all departments"""
    today = timezone.now().date()
    selected_date = request.GET.get('date', today.isoformat())
    selected_department = request.GET.get('department', '')
    
    try:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        selected_date = today
    
    departments = Department.objects.filter(is_active=True)
    
    employees = Employee.objects.filter(status='active').select_related('user', 'department')
    if selected_department:
        employees = employees.filter(department_id=selected_department)
    
    employee_attendance = []
    for emp in employees:
        attendance = Attendance.objects.filter(employee=emp, date=selected_date).first()
        employee_attendance.append({
            'employee': emp,
            'attendance': attendance,
            'form': AttendanceForm(instance=attendance) if attendance else AttendanceForm(initial={'shift': emp.shift})
        })
    
    stats = {
        'total': employees.count(),
        'present': Attendance.objects.filter(date=selected_date, status='present', employee__in=employees).count(),
        'absent': Attendance.objects.filter(date=selected_date, status='absent', employee__in=employees).count(),
        'late': Attendance.objects.filter(date=selected_date, status='late', employee__in=employees).count(),
        'half_day': Attendance.objects.filter(date=selected_date, status='half_day', employee__in=employees).count(),
        'on_leave': Attendance.objects.filter(date=selected_date, status='on_leave', employee__in=employees).count(),
    }
    stats['unmarked'] = stats['total'] - (stats['present'] + stats['absent'] + stats['late'] + stats['half_day'] + stats['on_leave'])
    
    context = {
        'employee_attendance': employee_attendance,
        'departments': departments,
        'selected_date': selected_date,
        'selected_department': selected_department,
        'stats': stats,
        'today': today,
    }
    return render(request, 'hospital_hr/attendance_dashboard.html', context)


@login_required
@hr_or_admin_required
def attendance_mark(request, employee_id):
    """Mark or update attendance for a single employee (AJAX/Modal)"""
    employee = get_object_or_404(Employee, pk=employee_id)
    date_str = request.GET.get('date', timezone.now().date().isoformat())
    
    try:
        date = datetime.strptime(date_str, '%Y-%m-%d').date()
    except ValueError:
        date = timezone.now().date()
    
    attendance, created = Attendance.objects.get_or_create(
        employee=employee,
        date=date,
        defaults={
            'department': employee.department,
            'shift': employee.shift,
            'marked_by': request.user
        }
    )
    
    if request.method == 'POST':
        form = AttendanceForm(request.POST, instance=attendance)
        if form.is_valid():
            att = form.save(commit=False)
            att.marked_by = request.user
            att.department = employee.department
            att.save()
            messages.success(request, f'Attendance marked for {employee.get_full_name()}')
            return redirect(f"{request.META.get('HTTP_REFERER', 'hospital_hr:attendance_dashboard')}?date={date}")
    else:
        form = AttendanceForm(instance=attendance)
    
    context = {
        'form': form,
        'employee': employee,
        'date': date,
        'attendance': attendance,
    }
    return render(request, 'hospital_hr/attendance_mark_modal.html', context)


@login_required
@hr_or_admin_required
def attendance_bulk_mark(request):
    """Bulk mark attendance for multiple employees"""
    if request.method == 'POST':
        date_str = request.POST.get('date', timezone.now().date().isoformat())
        try:
            date = datetime.strptime(date_str, '%Y-%m-%d').date()
        except ValueError:
            date = timezone.now().date()
        
        employee_ids = request.POST.getlist('employee_ids')
        status = request.POST.get('status', 'present')
        shift = request.POST.get('shift', 'general')
        
        count = 0
        for emp_id in employee_ids:
            try:
                employee = Employee.objects.get(pk=emp_id)
                attendance, created = Attendance.objects.update_or_create(
                    employee=employee,
                    date=date,
                    defaults={
                        'department': employee.department,
                        'shift': shift,
                        'status': status,
                        'marked_by': request.user
                    }
                )
                count += 1
            except Employee.DoesNotExist:
                continue
        
        messages.success(request, f'Attendance marked for {count} employees')
        return redirect(f"hospital_hr:attendance_dashboard?date={date}")
    
    return redirect('hospital_hr:attendance_dashboard')


@login_required
@dept_head_or_admin_required
def attendance_department(request):
    """Department Head view - READ ONLY - only see their department"""
    today = timezone.now().date()
    selected_date = request.GET.get('date', today.isoformat())
    
    try:
        selected_date = datetime.strptime(selected_date, '%Y-%m-%d').date()
    except ValueError:
        selected_date = today
    
    user_department = None
    if request.user.role == 'dept_head':
        user_department = Department.objects.filter(head=request.user).first()
        if not user_department:
            messages.error(request, 'You are not assigned as head of any department.')
            return redirect('hospital_hr:dashboard')
        employees = Employee.objects.filter(department=user_department, status='active')
    else:
        employees = Employee.objects.filter(status='active')
        user_department = Department.objects.filter(is_active=True).first()
    
    employee_attendance = []
    for emp in employees:
        attendance = Attendance.objects.filter(employee=emp, date=selected_date).first()
        employee_attendance.append({
            'employee': emp,
            'attendance': attendance,
        })
    
    stats = {
        'total': employees.count(),
        'present': Attendance.objects.filter(date=selected_date, status='present', employee__in=employees).count(),
        'absent': Attendance.objects.filter(date=selected_date, status='absent', employee__in=employees).count(),
        'late': Attendance.objects.filter(date=selected_date, status='late', employee__in=employees).count(),
        'half_day': Attendance.objects.filter(date=selected_date, status='half_day', employee__in=employees).count(),
        'on_leave': Attendance.objects.filter(date=selected_date, status='on_leave', employee__in=employees).count(),
    }
    stats['unmarked'] = stats['total'] - (stats['present'] + stats['absent'] + stats['late'] + stats['half_day'] + stats['on_leave'])
    
    context = {
        'employee_attendance': employee_attendance,
        'department': user_department,
        'selected_date': selected_date,
        'stats': stats,
        'today': today,
        'is_read_only': request.user.role == 'dept_head',
    }
    return render(request, 'hospital_hr/attendance_department.html', context)




@login_required
def attendance_my_view(request):
    """Staff mark their own attendance with Check In/Check Out"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, 'No employee profile found for your account.')
        return redirect('hospital_hr:dashboard')
    
    today = timezone.now().date()
    now = timezone.now()
    
    # Get today's attendance
    today_attendance = Attendance.objects.filter(employee=employee, date=today).first()
    
    # Get recent attendance (last 30 days)
    start_date = today - timedelta(days=30)
    attendance_records = Attendance.objects.filter(
        employee=employee,
        date__gte=start_date,
        date__lte=today
    ).order_by('-date')
    
    stats = {
        'present': attendance_records.filter(status='present').count(),
        'absent': attendance_records.filter(status='absent').count(),
        'late': attendance_records.filter(status='late').count(),
        'half_day': attendance_records.filter(status='half_day').count(),
        'on_leave': attendance_records.filter(status='on_leave').count(),
    }
    stats['total_working_days'] = stats['present'] + stats['late'] + stats['half_day']
    
    context = {
        'employee': employee,
        'today_attendance': today_attendance,
        'attendance_records': attendance_records[:10],
        'stats': stats,
        'today': today,
        'now': now,
    }
    return render(request, 'hospital_hr/attendance_my_view.html', context)


@login_required
def attendance_check_in(request):
    """Staff check in"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, 'No employee profile found for your account.')
        return redirect('hospital_hr:dashboard')
    
    today = timezone.now().date()
    now = timezone.now()
    
    # Check if already checked in today
    attendance = Attendance.objects.filter(employee=employee, date=today).first()
    if attendance and attendance.check_in_time:
        messages.warning(request, 'You have already checked in today.')
        return redirect('hospital_hr:attendance_my_view')
    
    # Create or update attendance
    if not attendance:
        attendance = Attendance.objects.create(
            employee=employee,
            department=employee.department,
            date=today,
            shift=employee.shift,
            check_in_time=now.time(),
            status='present',
            marked_by=request.user
        )
        messages.success(request, f'Checked in successfully at {now.strftime("%H:%M")}')
    else:
        attendance.check_in_time = now.time()
        attendance.status = 'present'
        attendance.save()
        messages.success(request, f'Checked in successfully at {now.strftime("%H:%M")}')
    
    return redirect('hospital_hr:attendance_my_view')


@login_required
def attendance_check_out(request):
    """Staff check out"""
    try:
        employee = request.user.employee_profile
    except Employee.DoesNotExist:
        messages.error(request, 'No employee profile found for your account.')
        return redirect('hospital_hr:dashboard')
    
    today = timezone.now().date()
    now = timezone.now()
    
    # Get today's attendance
    attendance = Attendance.objects.filter(employee=employee, date=today).first()
    if not attendance or not attendance.check_in_time:
        messages.error(request, 'You must check in first before checking out.')
        return redirect('hospital_hr:attendance_my_view')
    
    if attendance.check_out_time:
        messages.warning(request, 'You have already checked out today.')
        return redirect('hospital_hr:attendance_my_view')
    
    # Update check out time
    attendance.check_out_time = now.time()
    attendance.save()
    messages.success(request, f'Checked out successfully at {now.strftime("%H:%M")}')
    
    return redirect('hospital_hr:attendance_my_view')


@login_required
@hr_or_admin_required
def attendance_report(request):
    """Attendance reports with filters and export"""
    today = timezone.now().date()
    start_date = request.GET.get('start_date', (today - timedelta(days=30)).isoformat())
    end_date = request.GET.get('end_date', today.isoformat())
    department_id = request.GET.get('department', '')
    employee_id = request.GET.get('employee', '')
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        start_date = today - timedelta(days=30)
        end_date = today
    
    attendance_qs = Attendance.objects.filter(date__gte=start_date, date__lte=end_date)
    
    if department_id:
        attendance_qs = attendance_qs.filter(department_id=department_id)
    if employee_id:
        attendance_qs = attendance_qs.filter(employee_id=employee_id)
    
    attendance_qs = attendance_qs.select_related('employee', 'employee__user', 'department', 'marked_by')
    
    stats = {
        'total_records': attendance_qs.count(),
        'present': attendance_qs.filter(status='present').count(),
        'absent': attendance_qs.filter(status='absent').count(),
        'late': attendance_qs.filter(status='late').count(),
        'half_day': attendance_qs.filter(status='half_day').count(),
        'on_leave': attendance_qs.filter(status='on_leave').count(),
    }
    
    if stats['total_records'] > 0:
        stats['attendance_rate'] = round((stats['present'] + stats['late'] + stats['half_day']) / stats['total_records'] * 100, 1)
    else:
        stats['attendance_rate'] = 0
    
    dept_stats = attendance_qs.values('department__name').annotate(
        total=Count('id'),
        present=Count('id', filter=Q(status='present')),
        absent=Count('id', filter=Q(status='absent')),
        late=Count('id', filter=Q(status='late')),
    ).order_by('department__name')
    
    form = AttendanceReportForm(initial={
        'start_date': start_date,
        'end_date': end_date,
        'department': department_id if department_id else None,
        'employee': employee_id if employee_id else None,
    })
    
    context = {
        'attendance_records': attendance_qs.order_by('-date', 'employee__user__first_name')[:500],
        'stats': stats,
        'dept_stats': dept_stats,
        'form': form,
        'start_date': start_date,
        'end_date': end_date,
        'departments': Department.objects.filter(is_active=True),
    }
    return render(request, 'hospital_hr/attendance_report.html', context)


@login_required
@hr_or_admin_required
def attendance_export_csv(request):
    """Export attendance data to CSV"""
    start_date = request.GET.get('start_date', (timezone.now().date() - timedelta(days=30)).isoformat())
    end_date = request.GET.get('end_date', timezone.now().date().isoformat())
    department_id = request.GET.get('department', '')
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        start_date = timezone.now().date() - timedelta(days=30)
        end_date = timezone.now().date()
    
    attendance_qs = Attendance.objects.filter(
        date__gte=start_date,
        date__lte=end_date
    ).select_related('employee', 'employee__user', 'department', 'marked_by')
    
    if department_id:
        attendance_qs = attendance_qs.filter(department_id=department_id)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="attendance_{start_date}_{end_date}.csv"'
    
    writer = csv.writer(response)
    writer.writerow([
        'Date', 'Employee ID', 'Employee Name', 'Department', 'Shift',
        'Status', 'Check In', 'Check Out', 'Working Hours', 'Marked By', 'Notes'
    ])
    
    for att in attendance_qs.order_by('date', 'employee__user__first_name'):
        writer.writerow([
            att.date.strftime('%Y-%m-%d'),
            att.employee.employee_id,
            att.employee.get_full_name(),
            att.department.name if att.department else '',
            att.get_shift_display(),
            att.get_status_display(),
            att.check_in_time.strftime('%H:%M') if att.check_in_time else '',
            att.check_out_time.strftime('%H:%M') if att.check_out_time else '',
            att.get_working_hours(),
            att.marked_by.get_full_name() if att.marked_by else '',
            att.notes,
        ])
    
    return response
