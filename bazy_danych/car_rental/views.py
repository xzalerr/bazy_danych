from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.contrib.auth.models import Group
from django.utils.timezone import now
from django.utils import timezone
from .models import Car, Reservation
from datetime import datetime

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
    from .models import User
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        phone_number = request.POST.get('phone_number')

        user = User.objects.create_user(username=username, password=password, phone_number=phone_number)
        user.groups.add(Group.objects.get(name='Client'))
        return JsonResponse({'message': 'Account created successfully!'})
    return render(request, 'client/create_account.html')

# Dodawanie rezerwacji
@permission_required('car_rental.add_reservation', raise_exception=True)
def add_reservation(request):
    if request.method == 'POST':
        # Pobierz dane z formularza
        car_id = request.POST.get('car_id')
        start_date = now().date()  # Dzisiejsza data
        end_date = request.POST.get('end_date')
        
        # Konwertowanie daty zakończenia z formularza na obiekt Date
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
        
        # Oblicz koszt na serwerze
        base_cost = 100  # Koszt za tydzień
        extra_day_cost = 20  # Koszt za dodatkowy dzień

        # Obliczenie liczby dni wynajmu
        rental_duration = (end_date - start_date).days
        if rental_duration < 0:
            return JsonResponse({'error': 'Data zakończenia nie może być wcześniejsza niż dzisiejsza.'}, status=400)

        # Oblicz koszt
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

        return redirect('view_cars')  # Po udanej rezerwacji przekierowanie do listy samochodów

    return render(request, 'client/add_reservation.html')

@permission_required('car_rental.view_reservation', raise_exception=True)
def view_reservations(request):
    reservations = Reservation.objects.filter(user=request.user)
    return render(request, 'client/view_reservations.html', {'reservations': reservations})

@permission_required('car_rental.view_reservation', raise_exception=True)
def reservation_details(request, reservation_id):
    # Pobranie rezerwacji na podstawie ID
    reservation = get_object_or_404(Reservation, id=reservation_id)

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
