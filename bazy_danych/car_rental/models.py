from django.db import models
from django.contrib.auth.models import AbstractUser

# Model dla samochodów
class Car(models.Model):
    brand = models.CharField(max_length=100) 
    model = models.CharField(max_length=100)  
    year_of_manufacture = models.IntegerField()  
    size = models.CharField(max_length=50)  
    purpose = models.CharField(max_length=100)  
    standard = models.CharField(max_length=50)  
    registration = models.CharField(max_length=20)

    class Meta:
        db_table = 'app_cars'

    def __str__(self):
        return f"{self.brand} {self.model} ({self.year_of_manufacture})"
    
# Model dla aut będących w naprawie
class Maintenance(models.Model):
    car = models.ForeignKey(Car, on_delete=models.CASCADE)
    maintenance_date = models.DateField()
    maintenance_description = models.CharField(max_length=50)
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    is_done = models.BooleanField(default=False)

    class Meta:
        db_table = 'app_maintenance'

    def __str__(self):
        return self.car


# Model dla użytkowników (pracownicy, klienci)
class User(AbstractUser):  # Dziedziczenie z AbstractUser
    phone_number = models.CharField(max_length=20, blank=True) 

    class Meta:
        db_table = 'app_users'

    def __str__(self):
        return self.username
    
# Model dla rezerwacji
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    car = models.ForeignKey(Car, on_delete=models.CASCADE) 
    start_date = models.DateTimeField()  
    end_date = models.DateTimeField()  
    cost = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)  
    approved = models.BooleanField(default=False)  

    class Meta:
        db_table = 'app_reservations'

    def __str__(self):
        approval_status = "Zatwierdzona" if self.approved else "Niezatwierdzona"
        return f"Rezerwacja: {self.user} - {self.car} od {self.start_date} do {self.end_date} ({approval_status})"
