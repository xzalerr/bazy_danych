from django.contrib.auth.decorators import permission_required, login_required, user_passes_test
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.models import Group
from django.contrib import messages
from django.utils.timezone import now
from django.utils import timezone
from .models import Car, Reservation, User
from datetime import datetime
from django.db import IntegrityError

def is_employee(user):
    return user.groups.filter(name='Employee').exists()

@user_passes_test(is_employee, login_url='login')
def manage_reservations(request):
    reservations = Reservation.objects.all()
    for reservation in reservations:
        reservation.is_finished = reservation.end_date <= now()
    return render(request, 'employee/manage_reservations.html', {'reservations': reservations})

@user_passes_test(is_employee, login_url='login')
def end_reservation(request, reservation_id):
    reservation = get_object_or_404(Reservation, id=reservation_id)
    reservation.delete()
    return redirect('manage_reservations')

@login_required
def home(request):
    return render(request, 'client/home.html', {'user': request.user})

# Wyświetlenie listy aut
@permission_required('car_rental.view_car', raise_exception=True)
def view_cars(request):
    cars = Car.objects.all()
    cars_with_availability = []
    for car in cars:
        # Sprawdzanie dostępności samochodu
        is_available = not Reservation.objects.filter(car=car, end_date__gte=now()).exists()
        cars_with_availability.append({
            'car': car,
            'is_available': is_available,
        })
    return render(request, 'client/view_cars.html', {'cars_with_availability': cars_with_availability})

@permission_required('car_rental.view_car', raise_exception=True)
def car_details(request, car_id):
    # Pobranie samochodu
    car = get_object_or_404(Car, id=car_id)

    # Sprawdzanie dostępności samochodu
    is_available = not Reservation.objects.filter(car=car, end_date__gte=now()).exists()

    return render(request, 'client/car_details.html', {
        'car': car,
        'is_available': is_available,  # Przekazanie dostępności
    })


# Utworzenie konta
def create_client_account(request):
    if request.method == 'POST':
        # Pobieranie danych z formularza
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        if not phone_number.isdigit() or int(phone_number) <= 0:
            messages.error(request, "Numer telefonu musi być dodatnią liczbą.")
            return render(request, 'client/create_account.html')
        # Sprawdzanie, czy użytkownik o podanym loginie lub numerze telefonu już istnieje
        if User.objects.filter(username=username).exists():
            messages.error(request, "Nazwa użytkownika już istnieje. Wybierz inną.")
            return render(request, 'client/create_account.html')

        if User.objects.filter(phone_number=phone_number).exists():
            messages.error(request, "Numer telefonu już jest używany. Wprowadź inny numer.")
            return render(request, 'client/create_account.html')

        try:
            # Sprawdzenie, czy grupa 'Client' istnieje
            client_group, created = Group.objects.get_or_create(name='Client')

            # Tworzenie użytkownika i dodanie do grupy
            user = User.objects.create_user(username=username, password=password, phone_number=phone_number)
            user.groups.add(client_group)

            messages.success(request, "Konto zostało pomyślnie utworzone. Możesz się teraz zalogować.")
            return redirect('login')

        except IntegrityError:
            messages.error(request, "Wystąpił błąd podczas tworzenia konta. Spróbuj ponownie.")
            return render(request, 'client/create_account.html')

    # Renderowanie formularza HTML
    return render(request, 'client/create_account.html')

@permission_required('car_rental.add_car', raise_exception=True)
def add_car(request):
    if request.method == 'POST':
        brand = request.POST.get('brand')
        model = request.POST.get('model')
        year_of_manufacture = request.POST.get('year_of_manufacture')
        registration = request.POST.get('registration')

        # Sprawdzenie czy samochód o danym numerze rejestracyjnym istnieje
        if Car.objects.filter(registration=registration).exists():
            messages.error(request, f"Samochód z numerem rejestracyjnym {registration} już istnieje!")
        else:
            Car.objects.create(
                brand=brand,
                model=model,
                year_of_manufacture=year_of_manufacture,
                registration=registration
            )
            messages.success(request, "Samochód został pomyślnie dodany!")
            return redirect('add_car')

    return render(request, 'employee/add_car.html')

@permission_required('car_rental.change_car', raise_exception=True)
def edit_car(request, car_id):
    car = get_object_or_404(Car, id=car_id)

    if request.method == 'POST':
        if 'save' in request.POST:  # Przyciski z różnymi akcjami
            # Aktualizacja danych samochodu
            car.brand = request.POST.get('brand')
            car.model = request.POST.get('model')
            car.year_of_manufacture = request.POST.get('year_of_manufacture')
            car.registration = request.POST.get('registration')

            # Sprawdzenie, czy numer rejestracyjny jest unikalny
            if Car.objects.filter(registration=car.registration).exclude(id=car.id).exists():
                messages.error(request, "Samochód o podanym numerze rejestracyjnym już istnieje.")
            else:
                car.save()
                messages.success(request, "Dane samochodu zostały zaktualizowane pomyślnie.")

        elif 'delete' in request.POST:  # Usunięcie samochodu
            # Sprawdzenie, czy samochód jest aktualnie wypożyczony
            if Reservation.objects.filter(car=car, end_date__gte=timezone.now().date()).exists():
                messages.error(request, "Nie można usunąć samochodu, ponieważ jest aktualnie wypożyczony.")
            else:
                car.delete()
                messages.success(request, "Samochód został usunięty.")
                return redirect('view_cars')  # Powrót do listy samochodów po usunięciu

        return redirect('edit_car', car_id=car.id)

    return render(request, 'employee/edit_car.html', {'car': car})

# Dodawanie rezerwacji
@permission_required('car_rental.add_reservation', raise_exception=True)
def add_reservation(request):
    if request.method == 'POST':
        # Pobierz dane z formularza
        car_id = request.POST.get('car_id')
        start_date = now().date()  # Dzisiejsza data
        end_date = request.POST.get('end_date')
        
        try:
            # Konwertowanie daty zakończenia z formularza na obiekt Date
            end_date = datetime.strptime(end_date, '%Y-%m-%d').date()

            # Obliczenie liczby dni wynajmu
            rental_duration = (end_date - start_date).days
            if rental_duration < 0:
                messages.error(request, "Data zakończenia nie może być wcześniejsza niż dzisiejsza.")
                car = get_object_or_404(Car, id=car_id)
                return redirect('car_details', car_id=car.id)

            # Oblicz koszt na serwerze
            base_cost = 100  # Koszt za tydzień
            extra_day_cost = 20  # Koszt za dodatkowy dzień
            if rental_duration <= 7:
                total_cost = base_cost
            else:
                total_cost = base_cost + (rental_duration - 7) * extra_day_cost

            # Pobierz samochód z bazy danych
            car = get_object_or_404(Car, id=car_id)

            # Utwórz nową rezerwację
            reservation = Reservation.objects.create(
                user=request.user,
                car=car,
                start_date=start_date,
                end_date=end_date,
                cost=total_cost
            )

            messages.success(request, "Rezerwacja została pomyślnie utworzona.")
            return redirect('view_cars')  # Po udanej rezerwacji przekierowanie do listy samochodów

        except ValueError:
            messages.error(request, "Nieprawidłowy format daty zakończenia.")
            car = get_object_or_404(Car, id=car_id)
            return redirect('car_details', car_id=car.id)

    return redirect('car_details', car_id=car.id)


@permission_required('car_rental.view_reservation', raise_exception=True)
def view_reservations(request):
    reservations = Reservation.objects.filter(user=request.user)
    for reservation in reservations:
        reservation.is_finished = reservation.end_date <= now()
    return render(request, 'client/view_reservations.html', {'reservations': reservations})

@permission_required('car_rental.view_reservation', raise_exception=True)
def reservation_details(request, reservation_id):
    # Pobranie rezerwacji na podstawie ID
    reservation = get_object_or_404(Reservation, id=reservation_id)
    reservation.is_finished = reservation.end_date <= now()
    # Sprawdzenie, czy rezerwacja jest jeszcze aktywna
    if reservation.end_date < reservation.start_date:
        return redirect('view_reservations')

    # Zakończenie rezerwacji
    if request.method == 'POST':
        reservation.delete()
        return redirect('view_reservations')  # Po zakończeniu przekierowanie do listy rezerwacji

    return render(request, 'client/reservation_details.html', {'reservation': reservation})

# Usuwanie rezerwacji
@permission_required('car_rental.delete_reservation', raise_exception=True)
def delete_reservation(request, reservation_id):
    from .models import Reservation
    reservation = Reservation.objects.get(id=reservation_id, user=request.user)
    reservation.delete()
    return JsonResponse({'message': 'Reservation deleted successfully!'})

# Edycja rezerwacji
@permission_required('car_rental.change_reservation', raise_exception=True)
def edit_reservation(request, reservation_id):
    from .models import Reservation
    reservation = Reservation.objects.get(id=reservation_id, user=request.user)
    if request.method == 'POST':
        reservation.start_date = request.POST.get('start_date')
        reservation.end_date = request.POST.get('end_date')
        reservation.save()
        return JsonResponse({'message': 'Reservation updated successfully!'})
    return render(request, 'client/edit_reservation.html', {'reservation': reservation})

# Wyświetlenie płatności
@permission_required('car_rental.view_payment', raise_exception=True)
def view_payment(request, reservation_id):
    from .models import Payment
    payment = Payment.objects.get(reservation_id=reservation_id, reservation__user=request.user)
    return render(request, 'client/view_payment.html', {'payment': payment})
