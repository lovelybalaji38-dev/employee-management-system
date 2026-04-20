from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_select_view, name='login_select'),
    path('login/employee/', views.employee_login_view, name='employee_login'),
    path('login/hr/', views.hr_login_view, name='hr_login'),
    path('login/admin/', views.admin_login_view, name='admin_login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    
    # Dashboards
    path('dashboard/admin/', views.admin_dashboard, name='admin_dashboard'),
    path('dashboard/hr/', views.hr_dashboard, name='hr_dashboard'),
    path('dashboard/employee/', views.employee_dashboard, name='employee_dashboard'),
    
    # HR Management (Admin Only)
    path('manage-hr/', views.manage_hr, name='manage_hr'),
    path('manage-hr/add/', views.add_hr, name='add_hr'),
    
    # Employee Management (Admin/HR)
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/add/', views.add_employee, name='add_employee'),
    path('employees/<int:pk>/', views.employee_detail, name='employee_detail'),
    path('employees/<int:pk>/edit/', views.edit_employee, name='edit_employee'),
    path('employees/<int:pk>/delete/', views.delete_employee, name='delete_employee'),
    
    # Task Management
    path('tasks/', views.task_list, name='task_list'),
    path('tasks/add/', views.add_task, name='add_task'),
    path('tasks/<int:pk>/update/', views.update_task_status, name='update_task_status'),
    
    # Profile
    path('profile/', views.profile, name='profile'),
]
