from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from functools import wraps


def role_required(*roles):
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect('hospital_hr:login')
            
            if request.user.role in roles or request.user.is_superuser:
                return view_func(request, *args, **kwargs)
            else:
                return redirect('hospital_hr:access_denied')
        
        return _wrapped_view
    return decorator


def admin_required(view_func):
    return role_required('admin')(view_func)


def hr_or_admin_required(view_func):
    return role_required('admin', 'hr')(view_func)


def dept_head_or_admin_required(view_func):
    return role_required('admin', 'dept_head')(view_func)


def staff_required(view_func):
    return role_required('admin', 'hr', 'dept_head', 'staff')(view_func)
