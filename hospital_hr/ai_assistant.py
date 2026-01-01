"""
AI Assistant Module for Amrita Hospital HRMS
Implements RAG (Retrieval-Augmented Generation) for HR queries
"""

import json
import re
from datetime import date, datetime, timedelta
from django.db.models import Count, Q, Avg, Sum
from django.conf import settings

from .models import Employee, Department, Attendance, LeaveRequest, Job, Application


class HRQueryProcessor:
    """
    Processes natural language queries and retrieves relevant data from the database.
    This class implements the RAG pattern - it retrieves data first, then sends to AI.
    """
    
    # Query patterns to identify intent
    QUERY_PATTERNS = {
        'leave_today': [
            r'on leave today', r'leave today', r'employees.*leave.*today',
            r'who.*on leave', r'how many.*leave'
        ],
        'absent_today': [
            r'absent today', r'absentees', r'who.*absent',
            r'how many.*absent', r'missing today'
        ],
        'attendance_summary': [
            r'attendance.*summary', r'attendance.*report', r'attendance.*status',
            r'present today', r'how many.*present'
        ],
        'department_attendance': [
            r'attendance.*department', r'department.*attendance',
            r'(\w+).*department.*absent', r'absent.*(\w+).*department',
            r'(\w+).*attendance'
        ],
        'employee_count': [
            r'how many employees', r'total employees', r'employee count',
            r'number of employees', r'staff count'
        ],
        'department_info': [
            r'department.*info', r'list.*departments', r'all departments',
            r'department.*details', r'which departments', r'show.*departments',
            r'department.*names', r'departments.*names', r'what.*departments',
            r'tell.*about.*departments', r'department.*list'
        ],
        'job_applications': [
            r'job applications', r'pending applications', r'how many.*applications',
            r'application.*status', r'recruitment.*status'
        ],
        'open_positions': [
            r'open positions', r'job openings', r'vacancies',
            r'open jobs', r'hiring'
        ],
        'leave_requests': [
            r'leave requests', r'pending.*leave', r'leave.*pending',
            r'leave.*approval', r'approve.*leave'
        ],
        'employee_by_department': [
            r'employees.*in.*(\w+)', r'(\w+).*employees',
            r'staff.*in.*(\w+)', r'list.*(\w+).*staff'
        ],
        'nurses': [
            r'nurses', r'nursing staff', r'nursing'
        ],
        'doctors': [
            r'doctors', r'medical staff', r'physicians'
        ],
    }
    
    def __init__(self, user):
        self.user = user
        self.today = date.today()
    
    def process_query(self, query: str) -> dict:
        """
        Process a natural language query and return relevant data context.
        Returns a dict with 'context' (data) and 'query_type' (identified intent).
        """
        query_lower = query.lower().strip()
        
        # Identify query intent
        query_type = self._identify_query_type(query_lower)
        
        # Fetch relevant data based on query type
        context_data = self._fetch_data(query_type, query_lower)
        
        return {
            'query_type': query_type,
            'context': context_data,
            'original_query': query,
            'timestamp': datetime.now().isoformat()
        }
    
    def _identify_query_type(self, query: str) -> str:
        """Identify the type of query based on patterns."""
        for query_type, patterns in self.QUERY_PATTERNS.items():
            for pattern in patterns:
                if re.search(pattern, query, re.IGNORECASE):
                    return query_type
        return 'general'
    
    def _fetch_data(self, query_type: str, query: str) -> dict:
        """Fetch relevant data from database based on query type."""
        
        if query_type == 'leave_today':
            return self._get_leave_today_data()
        elif query_type == 'absent_today':
            return self._get_absent_today_data()
        elif query_type == 'attendance_summary':
            return self._get_attendance_summary()
        elif query_type == 'department_attendance':
            return self._get_department_attendance(query)
        elif query_type == 'employee_count':
            return self._get_employee_count()
        elif query_type == 'department_info':
            return self._get_department_info()
        elif query_type == 'job_applications':
            return self._get_job_applications()
        elif query_type == 'open_positions':
            return self._get_open_positions()
        elif query_type == 'leave_requests':
            return self._get_leave_requests()
        elif query_type == 'employee_by_department':
            return self._get_employees_by_department(query)
        elif query_type == 'nurses':
            return self._get_nursing_staff()
        elif query_type == 'doctors':
            return self._get_medical_staff()
        else:
            return self._get_general_summary()
    
    def _get_leave_today_data(self) -> dict:
        """Get employees on leave today."""
        leaves = LeaveRequest.objects.filter(
            status='approved',
            start_date__lte=self.today,
            end_date__gte=self.today
        ).select_related('employee', 'employee__department', 'employee__user')
        
        leave_list = []
        for leave in leaves:
            leave_list.append({
                'employee_name': leave.employee.get_full_name(),
                'employee_id': leave.employee.employee_id,
                'department': leave.employee.department.name if leave.employee.department else 'N/A',
                'leave_type': leave.get_leave_type_display(),
                'start_date': leave.start_date.strftime('%Y-%m-%d'),
                'end_date': leave.end_date.strftime('%Y-%m-%d'),
            })
        
        return {
            'type': 'leave_today',
            'date': self.today.strftime('%Y-%m-%d'),
            'total_on_leave': len(leave_list),
            'employees': leave_list
        }
    
    def _get_absent_today_data(self) -> dict:
        """Get employees absent today."""
        absent_records = Attendance.objects.filter(
            date=self.today,
            status='absent'
        ).select_related('employee', 'department', 'employee__user')
        
        absent_list = []
        for record in absent_records:
            absent_list.append({
                'employee_name': record.employee.get_full_name(),
                'employee_id': record.employee.employee_id,
                'department': record.department.name,
                'designation': record.employee.designation,
            })
        
        # Also get employees with no attendance record today (potentially absent)
        employees_with_attendance = Attendance.objects.filter(
            date=self.today
        ).values_list('employee_id', flat=True)
        
        no_record = Employee.objects.filter(
            status='active'
        ).exclude(
            id__in=employees_with_attendance
        ).select_related('department', 'user')[:20]  # Limit for performance
        
        no_record_list = []
        for emp in no_record:
            no_record_list.append({
                'employee_name': emp.get_full_name(),
                'employee_id': emp.employee_id,
                'department': emp.department.name if emp.department else 'N/A',
                'designation': emp.designation,
            })
        
        return {
            'type': 'absent_today',
            'date': self.today.strftime('%Y-%m-%d'),
            'marked_absent': len(absent_list),
            'absent_employees': absent_list,
            'no_attendance_record': len(no_record_list),
            'employees_without_record': no_record_list
        }
    
    def _get_attendance_summary(self) -> dict:
        """Get attendance summary for today."""
        attendance_stats = Attendance.objects.filter(
            date=self.today
        ).values('status').annotate(count=Count('id'))
        
        stats_dict = {item['status']: item['count'] for item in attendance_stats}
        
        total_employees = Employee.objects.filter(status='active').count()
        total_marked = sum(stats_dict.values())
        
        return {
            'type': 'attendance_summary',
            'date': self.today.strftime('%Y-%m-%d'),
            'total_active_employees': total_employees,
            'total_attendance_marked': total_marked,
            'present': stats_dict.get('present', 0),
            'absent': stats_dict.get('absent', 0),
            'late': stats_dict.get('late', 0),
            'half_day': stats_dict.get('half_day', 0),
            'on_leave': stats_dict.get('on_leave', 0),
            'not_marked': total_employees - total_marked
        }
    
    def _get_department_attendance(self, query: str) -> dict:
        """Get attendance for a specific department or all departments."""
        # Try to extract department name from query
        dept_name = None
        departments = Department.objects.filter(is_active=True)
        
        for dept in departments:
            if dept.name.lower() in query.lower() or dept.code.lower() in query.lower():
                dept_name = dept.name
                break
        
        if dept_name:
            # Specific department
            dept = Department.objects.get(name=dept_name)
            attendance = Attendance.objects.filter(
                date=self.today,
                department=dept
            ).values('status').annotate(count=Count('id'))
            
            stats = {item['status']: item['count'] for item in attendance}
            total_staff = dept.get_staff_count()
            
            return {
                'type': 'department_attendance',
                'department': dept_name,
                'date': self.today.strftime('%Y-%m-%d'),
                'total_staff': total_staff,
                'present': stats.get('present', 0),
                'absent': stats.get('absent', 0),
                'late': stats.get('late', 0),
                'on_leave': stats.get('on_leave', 0),
            }
        else:
            # All departments summary
            dept_stats = []
            for dept in departments:
                attendance = Attendance.objects.filter(
                    date=self.today,
                    department=dept
                ).values('status').annotate(count=Count('id'))
                
                stats = {item['status']: item['count'] for item in attendance}
                dept_stats.append({
                    'department': dept.name,
                    'total_staff': dept.get_staff_count(),
                    'present': stats.get('present', 0),
                    'absent': stats.get('absent', 0),
                })
            
            return {
                'type': 'all_departments_attendance',
                'date': self.today.strftime('%Y-%m-%d'),
                'departments': dept_stats
            }
    
    def _get_employee_count(self) -> dict:
        """Get employee count statistics."""
        total = Employee.objects.count()
        active = Employee.objects.filter(status='active').count()
        on_leave = Employee.objects.filter(status='on_leave').count()
        
        by_category = Employee.objects.filter(status='active').values(
            'category'
        ).annotate(count=Count('id'))
        
        by_department = Employee.objects.filter(status='active').values(
            'department__name'
        ).annotate(count=Count('id')).order_by('-count')[:10]
        
        return {
            'type': 'employee_count',
            'total_employees': total,
            'active_employees': active,
            'on_leave': on_leave,
            'by_category': list(by_category),
            'by_department': list(by_department)
        }
    
    def _get_department_info(self) -> dict:
        """Get department information."""
        departments = Department.objects.filter(is_active=True)
        
        dept_list = []
        for dept in departments:
            dept_list.append({
                'name': dept.name,
                'code': dept.code,
                'location': dept.get_location_display(),
                'head': dept.head.get_full_name() if dept.head else 'Not Assigned',
                'staff_count': dept.get_staff_count(),
                'total_beds': dept.total_beds,
            })
        
        return {
            'type': 'department_info',
            'total_departments': len(dept_list),
            'departments': dept_list
        }
    
    def _get_job_applications(self) -> dict:
        """Get job application statistics."""
        total = Application.objects.count()
        by_status = Application.objects.values('status').annotate(count=Count('id'))
        
        recent = Application.objects.select_related('job').order_by('-applied_date')[:10]
        recent_list = []
        for app in recent:
            recent_list.append({
                'applicant': app.applicant_name,
                'job': app.job.title,
                'status': app.get_status_display(),
                'applied_date': app.applied_date.strftime('%Y-%m-%d'),
            })
        
        return {
            'type': 'job_applications',
            'total_applications': total,
            'by_status': list(by_status),
            'recent_applications': recent_list
        }
    
    def _get_open_positions(self) -> dict:
        """Get open job positions."""
        open_jobs = Job.objects.filter(status='open').select_related('department')
        
        jobs_list = []
        for job in open_jobs:
            jobs_list.append({
                'title': job.title,
                'department': job.department.name,
                'vacancies': job.vacancies,
                'applications': job.get_application_count(),
                'posted_date': job.posted_date.strftime('%Y-%m-%d'),
            })
        
        return {
            'type': 'open_positions',
            'total_open_jobs': len(jobs_list),
            'jobs': jobs_list
        }
    
    def _get_leave_requests(self) -> dict:
        """Get leave request statistics."""
        pending = LeaveRequest.objects.filter(status='pending').count()
        
        pending_list = LeaveRequest.objects.filter(
            status='pending'
        ).select_related('employee', 'employee__department', 'employee__user').order_by('-created_at')[:10]
        
        requests = []
        for req in pending_list:
            requests.append({
                'employee': req.employee.get_full_name(),
                'department': req.employee.department.name if req.employee.department else 'N/A',
                'leave_type': req.get_leave_type_display(),
                'start_date': req.start_date.strftime('%Y-%m-%d'),
                'end_date': req.end_date.strftime('%Y-%m-%d'),
                'days': req.total_days,
            })
        
        return {
            'type': 'leave_requests',
            'total_pending': pending,
            'pending_requests': requests
        }
    
    def _get_employees_by_department(self, query: str) -> dict:
        """Get employees in a specific department."""
        departments = Department.objects.filter(is_active=True)
        target_dept = None
        
        for dept in departments:
            if dept.name.lower() in query.lower() or dept.code.lower() in query.lower():
                target_dept = dept
                break
        
        if target_dept:
            employees = Employee.objects.filter(
                department=target_dept,
                status='active'
            ).select_related('user')
            
            emp_list = []
            for emp in employees:
                emp_list.append({
                    'name': emp.get_full_name(),
                    'employee_id': emp.employee_id,
                    'designation': emp.designation,
                    'category': emp.get_category_display(),
                })
            
            return {
                'type': 'employees_by_department',
                'department': target_dept.name,
                'total_employees': len(emp_list),
                'employees': emp_list
            }
        
        return {
            'type': 'employees_by_department',
            'error': 'Department not found in query',
            'available_departments': [d.name for d in departments]
        }
    
    def _get_nursing_staff(self) -> dict:
        """Get nursing staff information."""
        nurses = Employee.objects.filter(
            category='nursing',
            status='active'
        ).select_related('department', 'user')
        
        nurse_list = []
        for nurse in nurses:
            nurse_list.append({
                'name': nurse.get_full_name(),
                'employee_id': nurse.employee_id,
                'department': nurse.department.name if nurse.department else 'N/A',
                'designation': nurse.designation,
                'shift': nurse.get_shift_display(),
            })
        
        # Get today's attendance for nurses
        nurse_ids = [n.id for n in nurses]
        attendance = Attendance.objects.filter(
            date=self.today,
            employee_id__in=nurse_ids
        ).values('status').annotate(count=Count('id'))
        
        att_stats = {item['status']: item['count'] for item in attendance}
        
        return {
            'type': 'nursing_staff',
            'total_nurses': len(nurse_list),
            'nurses': nurse_list[:20],  # Limit for response size
            'today_attendance': {
                'present': att_stats.get('present', 0),
                'absent': att_stats.get('absent', 0),
                'on_leave': att_stats.get('on_leave', 0),
            }
        }
    
    def _get_medical_staff(self) -> dict:
        """Get medical staff (doctors) information."""
        doctors = Employee.objects.filter(
            category='medical',
            status='active'
        ).select_related('department', 'user')
        
        doctor_list = []
        for doc in doctors:
            doctor_list.append({
                'name': doc.get_full_name(),
                'employee_id': doc.employee_id,
                'department': doc.department.name if doc.department else 'N/A',
                'designation': doc.designation,
                'specialization': doc.specialization,
            })
        
        return {
            'type': 'medical_staff',
            'total_doctors': len(doctor_list),
            'doctors': doctor_list[:20]  # Limit for response size
        }
    
    def _get_general_summary(self) -> dict:
        """Get a general HR summary when query type is unclear."""
        # Get all departments with details
        departments = Department.objects.filter(is_active=True)
        dept_list = []
        for dept in departments:
            dept_list.append({
                'name': dept.name,
                'code': dept.code,
                'location': dept.get_location_display(),
                'head': dept.head.get_full_name() if dept.head else 'Not Assigned',
                'staff_count': dept.get_staff_count(),
                'total_beds': dept.total_beds,
            })
        
        # Get employee breakdown by department
        emp_by_dept = Employee.objects.filter(status='active').values(
            'department__name'
        ).annotate(count=Count('id')).order_by('-count')
        
        # Get employee breakdown by category
        emp_by_category = Employee.objects.filter(status='active').values(
            'category'
        ).annotate(count=Count('id'))
        
        return {
            'type': 'general_summary',
            'date': self.today.strftime('%Y-%m-%d'),
            'employees': {
                'total': Employee.objects.count(),
                'active': Employee.objects.filter(status='active').count(),
                'on_leave': Employee.objects.filter(status='on_leave').count(),
                'by_department': list(emp_by_dept),
                'by_category': list(emp_by_category),
            },
            'departments': {
                'total': len(dept_list),
                'list': dept_list,
            },
            'attendance_today': {
                'marked': Attendance.objects.filter(date=self.today).count(),
                'present': Attendance.objects.filter(date=self.today, status='present').count(),
                'absent': Attendance.objects.filter(date=self.today, status='absent').count(),
                'late': Attendance.objects.filter(date=self.today, status='late').count(),
                'on_leave': Attendance.objects.filter(date=self.today, status='on_leave').count(),
            },
            'leave_requests': {
                'pending': LeaveRequest.objects.filter(status='pending').count(),
                'approved': LeaveRequest.objects.filter(status='approved').count(),
                'rejected': LeaveRequest.objects.filter(status='rejected').count(),
                'on_leave_today': LeaveRequest.objects.filter(
                    status='approved',
                    start_date__lte=self.today,
                    end_date__gte=self.today
                ).count(),
            },
            'recruitment': {
                'open_positions': Job.objects.filter(status='open').count(),
                'closed_positions': Job.objects.filter(status='closed').count(),
                'total_applications': Application.objects.count(),
                'pending_applications': Application.objects.filter(status='submitted').count(),
                'shortlisted': Application.objects.filter(status='shortlisted').count(),
                'rejected_applications': Application.objects.filter(status='rejected').count(),
            }
        }


class GroqAIClient:
    """
    Client for interacting with Groq API.
    Sends context data and receives natural language responses.
    """
    
    def __init__(self, api_key: str = None):
        self.api_key = api_key or getattr(settings, 'GROQ_API_KEY', None)
        self.api_url = "https://api.groq.com/openai/v1/chat/completions"
        self.model = "llama-3.1-8b-instant"  # Fast and capable model
    
    def generate_response(self, query: str, context: dict) -> str:
        """
        Generate a natural language response using Groq API.
        """
        if not self.api_key:
            return self._generate_fallback_response(query, context)
        
        import requests
        
        system_prompt = """You are an AI HR Assistant for Amrita Hospital HRMS. 
You help HR managers and administrators analyze workforce data.

IMPORTANT RULES:
1. ONLY use the data provided in the context. Never make up or guess information.
2. If the data doesn't contain the answer, say "I don't have that information in the current data."
3. Be concise and professional.
4. Format numbers and lists clearly.
5. If asked about something not in the context, explain what data IS available.
6. Always mention the date when discussing attendance or leave data.

You are speaking to an HR professional who needs accurate, actionable insights."""

        user_message = f"""User Question: {query}

HR Database Context (this is the ONLY data you can use):
{json.dumps(context, indent=2, default=str)}

Please provide a helpful, accurate response based ONLY on the above data."""

        try:
            headers = {
                "Authorization": f"Bearer {self.api_key}",
                "Content-Type": "application/json"
            }
            
            payload = {
                "model": self.model,
                "messages": [
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_message}
                ],
                "temperature": 0.3,  # Lower temperature for more factual responses
                "max_tokens": 1024
            }
            
            response = requests.post(
                self.api_url,
                headers=headers,
                json=payload,
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result['choices'][0]['message']['content']
            else:
                return self._generate_fallback_response(query, context)
                
        except Exception as e:
            return self._generate_fallback_response(query, context)
    
    def _generate_fallback_response(self, query: str, context: dict) -> str:
        """
        Generate a response without API when key is not available.
        Uses template-based responses.
        """
        context_type = context.get('type', 'general')
        
        if context_type == 'leave_today':
            total = context.get('total_on_leave', 0)
            employees = context.get('employees', [])
            if total == 0:
                return f"No employees are on approved leave today ({context.get('date', 'today')})."
            
            response = f"**{total} employee(s) on leave today** ({context.get('date', '')}):\n\n"
            for emp in employees[:10]:
                response += f"- **{emp['employee_name']}** ({emp['department']}) - {emp['leave_type']}\n"
            return response
        
        elif context_type == 'absent_today':
            marked = context.get('marked_absent', 0)
            no_record = context.get('no_attendance_record', 0)
            
            response = f"**Absence Report for {context.get('date', 'today')}:**\n\n"
            response += f"- Marked Absent: **{marked}**\n"
            response += f"- No Attendance Record: **{no_record}**\n\n"
            
            if context.get('absent_employees'):
                response += "**Absent Employees:**\n"
                for emp in context['absent_employees'][:10]:
                    response += f"- {emp['employee_name']} ({emp['department']})\n"
            
            return response
        
        elif context_type == 'attendance_summary':
            response = f"**Attendance Summary for {context.get('date', 'today')}:**\n\n"
            response += f"- Total Active Employees: **{context.get('total_active_employees', 0)}**\n"
            response += f"- Present: **{context.get('present', 0)}**\n"
            response += f"- Absent: **{context.get('absent', 0)}**\n"
            response += f"- Late: **{context.get('late', 0)}**\n"
            response += f"- On Leave: **{context.get('on_leave', 0)}**\n"
            response += f"- Not Marked: **{context.get('not_marked', 0)}**\n"
            return response
        
        elif context_type == 'employee_count':
            response = f"**Employee Statistics:**\n\n"
            response += f"- Total Employees: **{context.get('total_employees', 0)}**\n"
            response += f"- Active: **{context.get('active_employees', 0)}**\n"
            response += f"- On Leave: **{context.get('on_leave', 0)}**\n\n"
            
            if context.get('by_department'):
                response += "**By Department:**\n"
                for dept in context['by_department'][:5]:
                    response += f"- {dept['department__name']}: {dept['count']}\n"
            
            return response
        
        elif context_type == 'department_info':
            response = f"**{context.get('total_departments', 0)} Active Departments:**\n\n"
            for dept in context.get('departments', []):
                response += f"- **{dept['name']}** ({dept['code']}): {dept['staff_count']} staff, Head: {dept['head']}\n"
            return response
        
        elif context_type == 'job_applications':
            response = f"**Job Applications Summary:**\n\n"
            response += f"- Total Applications: **{context.get('total_applications', 0)}**\n\n"
            
            if context.get('by_status'):
                response += "**By Status:**\n"
                for status in context['by_status']:
                    response += f"- {status['status'].replace('_', ' ').title()}: {status['count']}\n"
            
            return response
        
        elif context_type == 'open_positions':
            jobs = context.get('jobs', [])
            response = f"**{context.get('total_open_jobs', 0)} Open Positions:**\n\n"
            for job in jobs:
                response += f"- **{job['title']}** ({job['department']}): {job['vacancies']} vacancies, {job['applications']} applications\n"
            return response
        
        elif context_type == 'leave_requests':
            response = f"**{context.get('total_pending', 0)} Pending Leave Requests:**\n\n"
            for req in context.get('pending_requests', []):
                response += f"- **{req['employee']}** ({req['department']}): {req['leave_type']} from {req['start_date']} to {req['end_date']} ({req['days']} days)\n"
            return response
        
        elif context_type == 'nursing_staff':
            response = f"**Nursing Staff Summary:**\n\n"
            response += f"- Total Nurses: **{context.get('total_nurses', 0)}**\n"
            att = context.get('today_attendance', {})
            response += f"- Present Today: **{att.get('present', 0)}**\n"
            response += f"- Absent Today: **{att.get('absent', 0)}**\n"
            return response
        
        elif context_type == 'general_summary':
            response = f"**HR Dashboard Summary ({context.get('date', 'today')}):**\n\n"
            
            # Departments
            depts = context.get('departments', {})
            dept_list = depts.get('list', [])
            response += f"**Departments ({depts.get('total', 0)}):**\n"
            for dept in dept_list:
                response += f"- **{dept['name']}** ({dept['code']}): {dept['staff_count']} staff, Head: {dept['head']}, Location: {dept['location']}\n"
            response += "\n"
            
            # Employees
            emp = context.get('employees', {})
            response += f"**Employees:** {emp.get('active', 0)} active / {emp.get('total', 0)} total\n"
            if emp.get('by_department'):
                response += "**By Department:**\n"
                for dept in emp['by_department'][:5]:
                    response += f"  - {dept['department__name']}: {dept['count']}\n"
            response += "\n"
            
            # Attendance
            att = context.get('attendance_today', {})
            response += f"**Today's Attendance:** {att.get('present', 0)} present, {att.get('absent', 0)} absent, {att.get('late', 0)} late\n\n"
            
            # Leave
            leave = context.get('leave_requests', {})
            response += f"**Leave:** {leave.get('pending', 0)} pending requests, {leave.get('on_leave_today', 0)} on leave today\n\n"
            
            # Recruitment
            rec = context.get('recruitment', {})
            response += f"**Recruitment:** {rec.get('open_positions', 0)} open positions, {rec.get('pending_applications', 0)} pending applications\n"
            
            return response
        
        else:
            return "I've retrieved the relevant data. Please ask a more specific question about employees, attendance, leaves, or recruitment."
