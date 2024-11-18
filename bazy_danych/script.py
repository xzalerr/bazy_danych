import os
import django

# Ustawienia Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'bazy_danych.settings')
django.setup()

# Import modeli
from car_rental.models import Car

# Funkcja "main"
def main():
    print("Dodajemy samochody do bazy danych...")
    # Dodanie samochodów
    Car.objects.create(
        brand="Toyota",
        model="Yaris",
        year_of_manufacture=2020,
        size="small",
        purpose="city travel",
        standard="medium",
        registration="DW11223"
    )
    Car.objects.create(
        brand="Mercedes",
        model="Vito",
        year_of_manufacture=2000,
        size="x-large",
        purpose="transport",
        standard="low",
        registration="DW12345"
    )
    # Dodanie dwóch nowych samochodów
    Car.objects.create(
        brand="BMW",
        model="X5",
        year_of_manufacture=2021,
        size="large",
        purpose="luxury travel",
        standard="high",
        registration="DW98765"
    )
    Car.objects.create(
        brand="Audi",
        model="A4",
        year_of_manufacture=2022,
        size="medium",
        purpose="business",
        standard="medium",
        registration="DW87654"
    )
    print("Gotowe!")

    # Modyfikacja danych
    print("\nModyfikujemy dane samochodu...")
    car_to_update = Car.objects.get(registration="DW12345")
    car_to_update.purpose = "cargo transport"
    car_to_update.save()
    print(f"Zaktualizowano samochód: {car_to_update}")

    # Usuwanie danych
    print("\nUsuwamy samochód...")
    car_to_delete = Car.objects.get(registration="DW11223")
    car_to_delete.delete()
    print(f"Usunięto samochód: {car_to_delete}")

if __name__ == "__main__":
    main()
