import os
import django

# Ustawienia Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bazy_danych.settings')
django.setup()

# Import modeli
from car_rental.models import Car, Maintenance, Reservation, User
from django.utils.timezone import now, timedelta

# Funkcja "main"
def main():
    # # Dodanie samochodu
    # print("Dodawanie nowego samochodu...")
    # Car.objects.create(
    #     brand="Toyota",
    #     model="Yaris",
    #     year_of_manufacture=2020,
    #     size="Extra Large",
    #     purpose="city travel",
    #     standard="medium",
    #     registration="DW11223"
    # )

    # # Aktualizacja danych samochodu
    # print("Aktualizacja rozmiaru samochodu...")
    # car_to_update = Car.objects.get(registration="DW11223")
    # car_to_update.size = "Small"
    # car_to_update.save()

    # # Dodanie naprawy
    # print("Dodanie naprawy dla Yarisa...")
    # yaris = Car.objects.get(registration="DW11223")
    # maintenance = Maintenance.objects.create(
    #     car=yaris,
    #     maintenance_date=now().date(),
    #     maintenance_description="Brake check",
    #     cost=500.00,
    #     is_done=False
    # )

    # # Aktualizacja naprawy
    # maintenance.is_done = True
    # maintenance.save()

    # # Dodanie rezerwacji
    # print("Dodawanie rezerwacji dla użytkownika...")
    # user = User.objects.get(id=2)  # Zakładamy, że użytkownik o `id=2` istnieje
    # start_date = now() + timedelta(days=1)
    # end_date = start_date + timedelta(days=7)
    # reservation = Reservation.objects.create(
    #     user=user,
    #     car=yaris,
    #     start_date=start_date,
    #     end_date=end_date,
    #     cost=1500.00,
    #     approved=False
    # )

    # # Aktualizacja rezerwacji
    # reservation.approved = True
    # reservation.save()

    # Usunięcie danych
    print("Usuwanie danych...")
    user = User.objects.get(id=2)
    yaris = Car.objects.get(registration="DW11223")
    reservation = Reservation.objects.get(id=18)
    reservation.delete()
    maintenance = Maintenance.objects.get(car=yaris)
    maintenance.delete()
    yaris.delete()
    print("Dane usunięte pomyślnie.")

if __name__ == "__main__":
    main()
