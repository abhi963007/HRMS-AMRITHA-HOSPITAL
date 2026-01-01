from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User, Department, Employee, Job, Application, LeaveRequest, Attendance


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'employee_id', 'is_active']
    list_filter = ['role', 'is_active', 'is_staff', 'date_joined']
    search_fields = ['username', 'email', 'first_name', 'last_name', 'employee_id']
    
    fieldsets = BaseUserAdmin.fieldsets + (
        ('Hospital Information', {
            'fields': ('role', 'employee_id', 'phone', 'profile_picture'),
        }),
    )
    
    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Hospital Information', {
            'fields': ('role', 'employee_id', 'phone', 'email', 'first_name', 'last_name'),
        }),
    )


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['name', 'code', 'location', 'head', 'total_beds', 'is_active', 'created_at']
    list_filter = ['location', 'is_active', 'created_at']
    search_fields = ['name', 'code', 'description']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'code', 'location', 'head', 'description'),
        }),
        ('Contact Information', {
            'fields': ('phone', 'email'),
        }),
        ('Capacity', {
            'fields': ('total_beds',),
        }),
        ('Status', {
            'fields': ('is_active',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Employee)
class EmployeeAdmin(admin.ModelAdmin):
    list_display = ['employee_id', 'get_full_name', 'department', 'category', 'designation', 'shift', 'status', 'date_of_joining']
    list_filter = ['category', 'shift', 'status', 'department', 'date_of_joining']
    search_fields = ['employee_id', 'user__first_name', 'user__last_name', 'designation', 'qualification']
    readonly_fields = ['created_at', 'updated_at']
    
    fieldsets = (
        ('User Account', {
            'fields': ('user',),
        }),
        ('Employment Information', {
            'fields': ('employee_id', 'department', 'category', 'designation', 'shift', 'date_of_joining'),
        }),
        ('Personal Information', {
            'fields': ('date_of_birth',),
        }),
        ('Professional Details', {
            'fields': ('qualification', 'specialization', 'experience_years'),
        }),
        ('Compensation', {
            'fields': ('salary',),
        }),
        ('Emergency Contact', {
            'fields': ('emergency_contact_name', 'emergency_contact_phone', 'emergency_contact_relation'),
        }),
        ('Address', {
            'fields': ('address',),
        }),
        ('Status', {
            'fields': ('status',),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ['title', 'department', 'category', 'job_type', 'vacancies', 'status', 'posted_date', 'closing_date']
    list_filter = ['category', 'job_type', 'status', 'department', 'posted_date']
    search_fields = ['title', 'description', 'requirements']
    readonly_fields = ['posted_date', 'posted_by']
    
    fieldsets = (
        ('Job Information', {
            'fields': ('title', 'department', 'category', 'job_type', 'vacancies'),
        }),
        ('Job Description', {
            'fields': ('description', 'requirements', 'responsibilities'),
        }),
        ('Requirements', {
            'fields': ('min_experience', 'min_qualification'),
        }),
        ('Compensation', {
            'fields': ('salary_min', 'salary_max'),
        }),
        ('Status & Dates', {
            'fields': ('status', 'closing_date', 'posted_by', 'posted_date'),
        }),
    )


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ['applicant_name', 'job', 'email', 'phone', 'status', 'applied_date']
    list_filter = ['status', 'job__department', 'applied_date']
    search_fields = ['applicant_name', 'email', 'phone', 'qualification']
    readonly_fields = ['applied_date', 'updated_at']
    
    fieldsets = (
        ('Job Application', {
            'fields': ('job',),
        }),
        ('Applicant Information', {
            'fields': ('applicant_name', 'email', 'phone', 'date_of_birth'),
        }),
        ('Professional Details', {
            'fields': ('qualification', 'specialization', 'experience_years'),
        }),
        ('Current Employment', {
            'fields': ('current_employer', 'current_designation'),
        }),
        ('Application Materials', {
            'fields': ('resume', 'cover_letter'),
        }),
        ('Review', {
            'fields': ('status', 'interview_date', 'interview_notes', 'reviewed_by'),
        }),
        ('Timestamps', {
            'fields': ('applied_date', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(LeaveRequest)
class LeaveRequestAdmin(admin.ModelAdmin):
    list_display = ['employee', 'leave_type', 'start_date', 'end_date', 'total_days', 'status', 'created_at']
    list_filter = ['leave_type', 'status', 'start_date', 'end_date']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'reason']
    readonly_fields = ['created_at', 'updated_at', 'approval_date']
    
    fieldsets = (
        ('Employee', {
            'fields': ('employee',),
        }),
        ('Leave Details', {
            'fields': ('leave_type', 'start_date', 'end_date', 'total_days', 'reason'),
        }),
        ('Approval', {
            'fields': ('status', 'approved_by', 'approval_date', 'rejection_reason'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )


@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['date', 'employee', 'department', 'shift', 'status', 'check_in_time', 'check_out_time', 'marked_by']
    list_filter = ['status', 'shift', 'department', 'date']
    search_fields = ['employee__user__first_name', 'employee__user__last_name', 'employee__employee_id']
    readonly_fields = ['created_at', 'updated_at']
    date_hierarchy = 'date'
    
    fieldsets = (
        ('Employee & Date', {
            'fields': ('employee', 'department', 'date'),
        }),
        ('Attendance Details', {
            'fields': ('shift', 'status', 'check_in_time', 'check_out_time'),
        }),
        ('Additional Info', {
            'fields': ('notes', 'marked_by'),
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',),
        }),
    )
