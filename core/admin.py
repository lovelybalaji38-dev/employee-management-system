from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Department, Employee, Task

admin.site.register(User, UserAdmin)
admin.site.register(Department)
admin.site.register(Employee)
admin.site.register(Task)
