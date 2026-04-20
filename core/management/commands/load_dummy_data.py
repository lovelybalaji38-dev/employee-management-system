from django.core.management.base import BaseCommand
from core.models import User, Department, Employee, Task
from django.utils import timezone
from datetime import timedelta

class Command(BaseCommand):
    help = 'Loads dummy data for the Employee Management System'

    def handle(self, *args, **kwargs):
        self.stdout.write("Loading dummy data...")

        # Create Admin
        if not User.objects.filter(username='admin').exists():
            User.objects.create_superuser('admin', 'admin@example.com', 'admin123', first_name='System', last_name='Admin', role='Admin')
            self.stdout.write(self.style.SUCCESS('Admin user created.'))

        # Departments
        dev_dept, _ = Department.objects.get_or_create(name='Development')
        hr_dept, _ = Department.objects.get_or_create(name='Human Resources')
        design_dept, _ = Department.objects.get_or_create(name='Design')
        qa_dept, _ = Department.objects.get_or_create(name='Quality Assurance')
        mgmt_dept, _ = Department.objects.get_or_create(name='Management')

        employees_data = [
            {
                'first_name': 'Arjun', 'last_name': 'Kumar', 'email': 'arjun@ems.com',
                'role': 'Employee', 'salary': 40000, 'department': dev_dept,
                'task_title': 'Build API', 'task_desc': 'Develop RESTful API for mobile app.'
            },
            {
                'first_name': 'Priya', 'last_name': 'Sharma', 'email': 'priya@ems.com',
                'role': 'HR', 'salary': 35000, 'department': hr_dept,
                'task_title': 'Manage hiring', 'task_desc': 'Interview candidates for frontend developer role.'
            },
            {
                'first_name': 'Rahul', 'last_name': 'Verma', 'email': 'rahul@ems.com',
                'role': 'Admin', 'salary': 60000, 'department': mgmt_dept,
                'task_title': 'Team supervision', 'task_desc': 'Oversee the Q2 project deliveries.'
            },
            {
                'first_name': 'Sneha', 'last_name': 'Iyer', 'email': 'sneha@ems.com',
                'role': 'Employee', 'salary': 30000, 'department': design_dept,
                'task_title': 'UI Design', 'task_desc': 'Design mockups for the new dashboard.'
            },
            {
                'first_name': 'Karthik', 'last_name': 'Raj', 'email': 'karthik@ems.com',
                'role': 'Employee', 'salary': 28000, 'department': qa_dept,
                'task_title': 'Testing modules', 'task_desc': 'Perform integration testing on the payment module.'
            }
        ]

        for data in employees_data:
            if not User.objects.filter(username=data['email']).exists():
                user = User.objects.create_user(
                    username=data['email'],
                    email=data['email'],
                    password='password123',
                    first_name=data['first_name'],
                    last_name=data['last_name'],
                    role=data['role']
                )
                employee = Employee.objects.create(
                    user=user,
                    phone_number='9876543210',
                    department=data['department'],
                    salary=data['salary']
                )
                Task.objects.create(
                    title=data['task_title'],
                    description=data['task_desc'],
                    assigned_to=employee,
                    deadline=timezone.now() + timedelta(days=7),
                    status='Pending'
                )
                self.stdout.write(self.style.SUCCESS(f'Created employee {data["first_name"]} {data["last_name"]} with task.'))

        self.stdout.write(self.style.SUCCESS('Dummy data loaded successfully!'))
