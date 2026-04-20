from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.paginator import Paginator
from django.db.models import Q
from .models import User, Employee, Task, Department
from .forms import LoginForm, RegisterForm, EmployeeForm, TaskForm, TaskStatusForm, HRForm
from .decorators import admin_required, hr_required, employee_required, admin_or_hr_required

def get_dashboard_url(user):
    if user.is_superuser:
        return 'admin_dashboard'
    elif user.role == 'HR':
        return 'hr_dashboard'
    else:
        return 'employee_dashboard'

def home(request):
    if request.user.is_authenticated:
        return redirect(get_dashboard_url(request.user))
    return redirect('employee_login')

def login_select_view(request):
    if request.user.is_authenticated:
        return redirect(get_dashboard_url(request.user))
    return render(request, 'core/login_select.html')

def base_login_view(request, expected_role, template_name):
    if request.user.is_authenticated:
        return redirect(get_dashboard_url(request.user))
        
    if request.method == 'POST':
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            remember_me = form.cleaned_data.get('remember_me')
            
            user = authenticate(request, username=username, password=password)
            if user is not None:
                # Role validation based on the portal they are logging into
                if expected_role == 'Admin' and not (user.is_superuser or user.role == 'Admin'):
                    messages.error(request, "This portal is strictly for Administrators.")
                    return render(request, template_name, {'form': form})
                elif expected_role == 'HR' and user.role != 'HR':
                    messages.error(request, "This portal is strictly for HR users.")
                    return render(request, template_name, {'form': form})
                elif expected_role == 'Employee' and user.role != 'Employee':
                    messages.error(request, "This portal is strictly for Employees.")
                    return render(request, template_name, {'form': form})
                    
                login(request, user)
                if not remember_me:
                    request.session.set_expiry(0)
                else:
                    request.session.set_expiry(1209600)
                
                messages.success(request, f"Welcome back, {user.first_name or user.username}!")
                return redirect(get_dashboard_url(user))
            else:
                messages.error(request, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, template_name, {'form': form})

def employee_login_view(request):
    return base_login_view(request, 'Employee', 'core/employee_login.html')

def hr_login_view(request):
    return base_login_view(request, 'HR', 'core/hr_login.html')

def admin_login_view(request):
    return base_login_view(request, 'Admin', 'core/admin_login.html')

def logout_view(request):
    logout(request)
    messages.info(request, "You have successfully logged out.")
    return redirect('employee_login')

def register_view(request):
    if request.user.is_authenticated:
        return redirect(get_dashboard_url(request.user))
        
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
            user.role = 'Employee'
            user.save()
            
            Employee.objects.create(
                user=user,
                phone_number='',
                salary=0
            )
            
            messages.success(request, "Registration successful! You can now log in.")
            return redirect('employee_login')
    else:
        form = RegisterForm()
    return render(request, 'core/register.html', {'form': form})

from django.http import HttpResponseForbidden

@login_required
def admin_dashboard(request):

    # 🔥 ADD THIS HERE
    if not request.user.is_superuser:
        return HttpResponseForbidden()

    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status='Active').count()
    total_hr = User.objects.filter(role='HR').count()
    total_tasks = Task.objects.count()
    recent_tasks = Task.objects.order_by('-created_at')[:5]

    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'total_hr': total_hr,
        'total_tasks': total_tasks,
        'recent_tasks': recent_tasks,
    }

    return render(request, 'core/admin_dashboard.html', context)

@login_required
@hr_required
def hr_dashboard(request):
    total_employees = Employee.objects.count()
    active_employees = Employee.objects.filter(status='Active').count()
    my_assigned_tasks = Task.objects.filter(assigned_by=request.user).count()
    recent_tasks = Task.objects.order_by('-created_at')[:5]
    
    context = {
        'total_employees': total_employees,
        'active_employees': active_employees,
        'my_assigned_tasks': my_assigned_tasks,
        'recent_tasks': recent_tasks,
    }
    return render(request, 'core/hr_dashboard.html', context)

@login_required
@employee_required
def employee_dashboard(request):
    if not hasattr(request.user, 'employee_profile'):
        logout(request)
        messages.error(request, "Employee profile is missing or corrupted. Please contact the Administrator.")
        return redirect('employee_login')

    my_tasks = Task.objects.filter(assigned_to=request.user.employee_profile)
    pending_tasks = my_tasks.filter(status='Pending').count()
    completed_tasks = my_tasks.filter(status='Completed').count()
    recent_tasks = my_tasks.order_by('-deadline')[:5]
    
    context = {
        'pending_tasks': pending_tasks,
        'completed_tasks': completed_tasks,
        'total_tasks': my_tasks.count(),
        'recent_tasks': recent_tasks,
    }
    return render(request, 'core/employee_dashboard.html', context)

@login_required
@admin_required
def manage_hr(request):
    hrs = User.objects.filter(role='HR').order_by('-date_joined')
    return render(request, 'core/hr_list.html', {'hrs': hrs})

@login_required
@admin_required
def add_hr(request):
    if request.method == 'POST':
        form = HRForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data.get('password'))
            user.role = 'HR'
            user.save()
            messages.success(request, "HR User created successfully.")
            return redirect('manage_hr')
    else:
        form = HRForm()
    return render(request, 'core/hr_form.html', {'form': form, 'title': 'Create HR User'})

@login_required
@admin_or_hr_required
def employee_list(request):
    query = request.GET.get('q', '')
    employees = Employee.objects.all().order_by('-joining_date')
    
    if query:
        employees = employees.filter(
            Q(user__first_name__icontains=query) |
            Q(user__last_name__icontains=query) |
            Q(employee_id__icontains=query) |
            Q(department__name__icontains=query) |
            Q(user__role__icontains=query)
        )
        
    paginator = Paginator(employees, 6)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/employee_list.html', {'page_obj': page_obj, 'query': query})

@login_required
@admin_or_hr_required
def add_employee(request):
    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            email = form.cleaned_data.get('email')
            if User.objects.filter(email=email).exists() or User.objects.filter(username=email).exists():
                messages.error(request, "A user with this email already exists.")
            else:
                user = User.objects.create_user(
                    username=email,
                    email=email,
                    password='password123',
                    first_name=form.cleaned_data.get('first_name'),
                    last_name=form.cleaned_data.get('last_name'),
                    role=form.cleaned_data.get('role')
                )
                employee = form.save(commit=False)
                employee.user = user
                employee.save()
                messages.success(request, f"Employee {user.first_name} added successfully.")
                return redirect('employee_list')
    else:
        form = EmployeeForm()
    return render(request, 'core/employee_form.html', {'form': form, 'title': 'Add Employee'})

@login_required
@admin_or_hr_required
def edit_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.user.role == 'HR' and employee.user.role == 'Admin':
         messages.error(request, "HR cannot edit Admin profiles.")
         return redirect('employee_list')

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES, instance=employee)
        if form.is_valid():
            user = employee.user
            user.first_name = form.cleaned_data.get('first_name')
            user.last_name = form.cleaned_data.get('last_name')
            user.email = form.cleaned_data.get('email')
            user.role = form.cleaned_data.get('role')
            user.save()
            form.save()
            messages.success(request, "Employee updated successfully.")
            return redirect('employee_list')
    else:
        form = EmployeeForm(instance=employee)
    return render(request, 'core/employee_form.html', {'form': form, 'title': 'Edit Employee', 'employee': employee})

@login_required
@admin_or_hr_required
def delete_employee(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.user.role == 'HR' and employee.user.role == 'Admin':
        messages.error(request, "HR cannot delete Admin profiles.")
        return redirect('employee_list')
        
    if request.method == 'POST':
        user = employee.user
        user.delete()
        messages.success(request, "Employee deleted successfully.")
        return redirect('employee_list')
    return render(request, 'core/employee_confirm_delete.html', {'employee': employee})

@login_required
def employee_detail(request, pk):
    employee = get_object_or_404(Employee, pk=pk)
    if request.user.role == 'Employee' and request.user != employee.user:
        messages.error(request, "You can only view your own profile.")
        return redirect('employee_dashboard')
    return render(request, 'core/employee_detail.html', {'employee': employee})

@login_required
def task_list(request):
    if request.user.is_superuser or request.user.role == 'HR':
        tasks = Task.objects.all().order_by('-deadline')
    else:
        if not hasattr(request.user, 'employee_profile'):
            logout(request)
            messages.error(request, "Employee profile missing.")
            return redirect('employee_login')
        tasks = Task.objects.filter(assigned_to=request.user.employee_profile).order_by('-deadline')
        
    paginator = Paginator(tasks, 10)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    return render(request, 'core/task_list.html', {'page_obj': page_obj})

@login_required
@admin_or_hr_required
def add_task(request):
    if request.method == 'POST':
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.assigned_by = request.user
            task.save()
            messages.success(request, "Task assigned successfully.")
            return redirect('task_list')
    else:
        form = TaskForm()
    return render(request, 'core/task_form.html', {'form': form, 'title': 'Assign Task'})

@login_required
def update_task_status(request, pk):
    task = get_object_or_404(Task, pk=pk)
    
    if request.user.role == 'Employee':
        if not hasattr(request.user, 'employee_profile') or task.assigned_to.user != request.user:
            messages.error(request, "You can only update your own tasks.")
            return redirect('task_list')

    if request.method == 'POST':
        form = TaskStatusForm(request.POST, instance=task)
        if form.is_valid():
            form.save()
            messages.success(request, "Task status updated.")
            return redirect('task_list')
    else:
        form = TaskStatusForm(instance=task)
        
    return render(request, 'core/task_status_form.html', {'form': form, 'task': task})

@login_required
@employee_required
def profile(request):
    if not hasattr(request.user, 'employee_profile'):
        logout(request)
        messages.error(request, "Employee profile missing.")
        return redirect('employee_login')
    return render(request, 'core/profile.html', {'employee': request.user.employee_profile})
