from django.test import TestCase
from django.urls import reverse
from car_rental.models import User
from django.contrib.auth.models import Group
from car_rental.models import Car, Reservation
from django.utils import timezone

class ReservationViewsTest(TestCase):
    
    def setUp(self):
        # Create test users and add them to the appropriate groups
        self.client_user = User.objects.create_user(username='clientuser', password='password')
        self.client_group = Group.objects.create(name='Client')
        self.client_user.groups.add(self.client_group)
        
        self.employee_user = User.objects.create_user(username='employeeuser', password='password')
        self.employee_group = Group.objects.create(name='Employee')
        self.employee_user.groups.add(self.employee_group)

        # Create test cars
        self.car1 = Car.objects.create(make="Toyota", model="Corolla", year=2023, cost_per_day=50)
        self.car2 = Car.objects.create(make="Honda", model="Civic", year=2023, cost_per_day=60)

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
        data = {'car_id': self.car1.id, 'start_date': timezone.now(), 'end_date': timezone.now() + timezone.timedelta(days=1), 'cost': self.car1.cost_per_day}
        response = self.client.post(reverse('add_reservation'), data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reservation added successfully!')

    def test_add_reservation_as_employee(self):
        self.client.login(username='employeeuser', password='password')
        data = {'car_id': self.car1.id, 'start_date': timezone.now(), 'end_date': timezone.now() + timezone.timedelta(days=1), 'cost': self.car1.cost_per_day}
        response = self.client.post(reverse('add_reservation'), data)
        self.assertEqual(response.status_code, 403)  # Forbidden for non-clients

    def test_delete_reservation_as_client(self):
        self.client.login(username='clientuser', password='password')
        reservation = Reservation.objects.create(user=self.client_user, car=self.car1, start_date=timezone.now(), end_date=timezone.now() + timezone.timedelta(days=1), cost=self.car1.cost_per_day)
        response = self.client.post(reverse('delete_reservation', kwargs={'reservation_id': reservation.id}))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Reservation deleted successfully!')

    def test_delete_reservation_without_permission(self):
        self.client.login(username='employeeuser', password='password')
        reservation = Reservation.objects.create(user=self.client_user, car=self.car1, start_date=timezone.now(), end_date=timezone.now() + timezone.timedelta(days=1), cost=self.car1.cost_per_day)
        response = self.client.post(reverse('delete_reservation', kwargs={'reservation_id': reservation.id}))
        self.assertEqual(response.status_code, 403)  # Forbidden for non-client

