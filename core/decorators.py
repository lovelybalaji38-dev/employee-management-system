from django.contrib.auth.decorators import user_passes_test
from django.http import HttpResponseForbidden

def role_required(*allowed_roles):
    def check_role(user):
        if not user.is_authenticated:
            return False
        if user.is_superuser and 'Admin' in allowed_roles:
            return True
        if user.role in allowed_roles:
            return True
        return False
        
    def decorator(view_func):
        def _wrapped_view(request, *args, **kwargs):
            if not check_role(request.user):
                return HttpResponseForbidden("<h1>403 Forbidden</h1><p>You do not have permission to access this page.</p>")
            return view_func(request, *args, **kwargs)
        return _wrapped_view
    return decorator

# Pre-defined decorators
admin_required = role_required('Admin')
hr_required = role_required('HR')
employee_required = role_required('Employee')
admin_or_hr_required = role_required('Admin', 'HR')
