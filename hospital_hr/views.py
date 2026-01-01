from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import datetime, timedelta
from .models import User, Department, Employee, Job, Application, LeaveRequest
from .forms import (
    UserLoginForm, UserRegistrationForm, DepartmentForm, EmployeeForm,
    JobForm, ApplicationForm, ApplicationReviewForm, LeaveRequestForm, LeaveApprovalForm
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
        my_leaves = LeaveRequest.objects.filter(employee=employee).order_by('-created_at')[:10]
        approved_leaves = my_leaves.filter(status='approved').count()
        pending_leaves = my_leaves.filter(status='pending').count()
        rejected_leaves = my_leaves.filter(status='rejected').count()
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
