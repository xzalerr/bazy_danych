from django.test import TestCase
from django.urls import reverse
from car_rental.models import User, Car, Reservation
from django.contrib.auth.models import Group
from django.contrib.auth.models import Permission
from django.utils import timezone
from datetime import timedelta

class ReservationViewsTest(TestCase):
    
    def setUp(self):
        # Create test users and add them to the appropriate groups
        self.client_user = User.objects.create_user(username='clientuser', password='password')
        self.client_group = Group.objects.create(name='Client')
        self.client_user.groups.add(self.client_group)
        
        self.employee_user = User.objects.create_user(username='employeeuser', password='password')
        self.employee_group = Group.objects.create(name='Employee')
        self.employee_user.groups.add(self.employee_group)
        permission = Permission.objects.get(codename='add_reservation')
        self.client_user.user_permissions.add(permission)
        permission = Permission.objects.get(codename='view_car')
        self.client_user.user_permissions.add(permission)
        permission = Permission.objects.get(codename='delete_reservation')
        self.client_user.user_permissions.add(permission)
        self.employee_user.user_permissions.add(Permission.objects.get(codename='view_car'))
        # Create test cars
        self.car1 = Car.objects.create(
            brand="Toyota", 
            model="Corolla", 
            year_of_manufacture=2023, 
            size="Compact",
            purpose="Rental",
            standard="Standard",
            registration="XYZ1234"
        )
        self.car2 = Car.objects.create(
            brand="Honda", 
            model="Civic", 
            year_of_manufacture=2023, 
            size="Compact",
            purpose="Rental",
            standard="Standard",
            registration="ABC5678"
        )

    def test_view_cars_as_client(self):
        self.client.login(username='clientuser', password='password')
        response = self.client.get(reverse('view_cars'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'client/view_cars.html')

    def test_view_cars_as_employee(self):
        self.client.login(username='employeeuser', password='password')
        response = self.client.get(reverse('view_cars'))
        self.assertEqual(response.status_code, 200)

    def test_add_reservation_as_client(self):
        self.client.login(username='clientuser', password='password')
        # Zamiana end_date na poprawny format (tylko data, bez czasu i strefy czasowej)
        end_date = (timezone.now() + timedelta(days=1)).date()  # np. jutro
        data = {
            'car_id': self.car1.id, 
            'start_date': timezone.now().date(),  # dzisiejsza data
            'end_date': end_date,  # tylko data, np. jutro
            'cost': 100.00
        }
        response = self.client.post(reverse('add_reservation'), data)
        self.assertEqual(response.status_code, 302)  # Oczekiwane przekierowanie (302)
        self.assertRedirects(response, reverse('view_cars'))

    def test_add_reservation_as_employee(self):
        self.client.login(username='employeeuser', password='password')
        data = {
            'car_id': self.car1.id, 
            'start_date': timezone.now(), 
            'end_date': timezone.now() + timezone.timedelta(days=1), 
            'cost': 100.00
        }
        response = self.client.post(reverse('add_reservation'), data)
        self.assertEqual(response.status_code, 403)  # Forbidden for non-clients

    def test_delete_reservation_as_client(self):
        self.client.login(username='clientuser', password='password')
        reservation = Reservation.objects.create(
            user=self.client_user, 
            car=self.car1, 
            start_date=timezone.now(), 
            end_date=timezone.now() + timezone.timedelta(days=1), 
            cost=100.00
        )
        response = self.client.post(reverse('delete_reservation', kwargs={'reservation_id': reservation.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reservation deleted successfully!')

    def test_delete_reservation_without_permission(self):
        self.client.login(username='employeeuser', password='password')
        reservation = Reservation.objects.create(
            user=self.client_user, 
            car=self.car1, 
            start_date=timezone.now(), 
            end_date=timezone.now() + timezone.timedelta(days=1), 
            cost=100.00
        )
        response = self.client.post(reverse('delete_reservation', kwargs={'reservation_id': reservation.id}))
        self.assertEqual(response.status_code, 403)  # Forbidden for non-client
