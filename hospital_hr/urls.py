from django.urls import path
from . import views
from hrms.views_admin import fix_user_accounts

app_name = 'hospital_hr'

urlpatterns = [
    path('', views.landing_view, name='landing'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('dashboard/', views.dashboard_view, name='dashboard'),
    path('access-denied/', views.access_denied, name='access_denied'),
    
    # Admin utility to fix user accounts
    path('admin/fix-users/', fix_user_accounts, name='fix_users'),
    
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/<int:pk>/edit/', views.department_edit, name='department_edit'),
    path('departments/<int:pk>/delete/', views.department_delete, name='department_delete'),
    
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_create, name='employee_create'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.employee_edit, name='employee_edit'),
    path('employees/<int:pk>/delete/', views.employee_delete, name='employee_delete'),
    
    path('jobs/', views.job_list, name='job_list'),
    path('jobs/create/', views.job_create, name='job_create'),
    path('jobs/<int:pk>/', views.job_detail, name='job_detail'),
    path('jobs/<int:pk>/edit/', views.job_edit, name='job_edit'),
    path('jobs/<int:pk>/delete/', views.job_delete, name='job_delete'),
    
    path('careers/', views.job_public_list, name='job_public_list'),
    path('careers/<int:pk>/', views.job_public_detail, name='job_public_detail'),
    path('careers/<int:pk>/apply/', views.job_apply, name='job_apply'),
    
    path('applications/', views.application_list, name='application_list'),
    path('applications/<int:pk>/', views.application_detail, name='application_detail'),
    
    path('leave-requests/', views.leave_request_list, name='leave_request_list'),
    path('leave-requests/create/', views.leave_request_create, name='leave_request_create'),
    path('leave-requests/<int:pk>/approve/', views.leave_request_approve, name='leave_request_approve'),
    
    # Attendance Management
    path('attendance/', views.attendance_dashboard, name='attendance_dashboard'),
    path('attendance/mark/<int:employee_id>/', views.attendance_mark, name='attendance_mark'),
    path('attendance/bulk-mark/', views.attendance_bulk_mark, name='attendance_bulk_mark'),
    path('attendance/department/', views.attendance_department, name='attendance_department'),
    path('attendance/my/', views.attendance_my_view, name='attendance_my_view'),
    path('attendance/check-in/', views.attendance_check_in, name='attendance_check_in'),
    path('attendance/check-out/', views.attendance_check_out, name='attendance_check_out'),
    path('attendance/report/', views.attendance_report, name='attendance_report'),
    path('attendance/export/', views.attendance_export_csv, name='attendance_export_csv'),
]
