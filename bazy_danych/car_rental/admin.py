from django.contrib import admin
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType

# Register your models here.
def users_roles():
    client_group, _ = Group.objects.get_or_create(name="Client")
    employee_group, _ = Group.objects.get_or_create(name="Employee")

    car_ct = ContentType.objects.get(app_label='car_rental', model='car')
    maintenance_ct = ContentType.objects.get(app_label='car_rental', model='maintenance')
    user_ct = ContentType.objects.get(app_label='car_rental', model='user')
    reservation_ct = ContentType.objects.get(app_label='car_rental', model='reservation')

    client_perm = [
        Permission.objects.get(codename='view_car', content_type=car_ct),
        Permission.objects.get(codename='add_user', content_type=user_ct),
        Permission.objects.get(codename='add_reservation', content_type=reservation_ct),
        Permission.objects.get(codename='delete_reservation', content_type=reservation_ct),
        Permission.objects.get(codename='change_reservation', content_type=reservation_ct),
        Permission.objects.get(codename='view_reservation', content_type=reservation_ct)
    ]

    employee_perm = [
        Permission.objects.get(codename='add_car', content_type=car_ct),
        Permission.objects.get(codename='delete_car', content_type=car_ct),
        Permission.objects.get(codename='change_car', content_type=car_ct),
        Permission.objects.get(codename='view_car', content_type=car_ct),
        Permission.objects.get(codename='add_maintenance', content_type=maintenance_ct),
        Permission.objects.get(codename='delete_maintenance', content_type=maintenance_ct),
        Permission.objects.get(codename='change_maintenance', content_type=maintenance_ct),
        Permission.objects.get(codename='view_maintenance', content_type=maintenance_ct),
        Permission.objects.get(codename='view_user', content_type=user_ct),
        Permission.objects.get(codename='delete_reservation', content_type=reservation_ct),
        Permission.objects.get(codename='change_reservation', content_type=reservation_ct),
        Permission.objects.get(codename='view_reservation', content_type=reservation_ct)
    ]

    client_group.permissions.set(client_perm)
    employee_group.permissions.set(employee_perm)

    # Wywołanie w terminalu za pomocą Django Shell
    # python manage.py shell
    # >>> from car_rental.admin import users_roles
    # >>> users_roles()