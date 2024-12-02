from django.contrib.auth.decorators import permission_required
from django.shortcuts import render
from django.http import JsonResponse
from django.contrib.auth.models import Group

# Wyświetlenie listy aut
@permission_required('car_rental.view_car', raise_exception=True)
def view_cars(request):
    from .models import Car
    cars = Car.objects.all()
    return render(request, 'client/view_cars.html', {'cars': cars})

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
        from .models import Reservation, Car
        car_id = request.POST.get('car_id')
        start_date = request.POST.get('start_date')
        end_date = request.POST.get('end_date')
        cost = request.POST.get('cost')

        car = Car.objects.get(id=car_id)
        reservation = Reservation.objects.create(
            user=request.user, car=car, start_date=start_date, end_date=end_date, cost=cost
        )
        return JsonResponse({'message': 'Reservation added successfully!'})
    return render(request, 'client/add_reservation.html')

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
