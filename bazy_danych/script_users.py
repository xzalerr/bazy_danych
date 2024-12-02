import os
import django

# Set the DJANGO_SETTINGS_MODULE environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bazy_danych.settings')

# Initialize Django
django.setup()

from django.contrib.auth.models import Group
from car_rental.models import User as CustomUser  

# Create 3 clients
client1 = CustomUser.objects.create_user(username='client1', password='password1', phone_number='123456789')
client2 = CustomUser.objects.create_user(username='client2', password='password2', phone_number='987654321')
client3 = CustomUser.objects.create_user(username='client3', password='password3', phone_number='555555555')

# Create 1 employee
employee = CustomUser.objects.create_user(username='employee', password='employee123', phone_number='444444444')
employee.is_staff = True
employee.save()

# Get the groups created by users_roles
client_group = Group.objects.get(name='Client')
employee_group = Group.objects.get(name='Employee')

# Assign users to groups
client1.groups.add(client_group)
client2.groups.add(client_group)
client3.groups.add(client_group)

employee.groups.add(employee_group)

# Save users
client1.save()
client2.save()
client3.save()
employee.save()

print("Users and roles assigned successfully")
