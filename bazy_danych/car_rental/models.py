from django.db import models

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

# Model dla użytkowników (pracownicy, klienci)
class User(models.Model):
    username = models.CharField(max_length=150, unique=True)  
    email = models.EmailField(unique=True) 
    phone_number = models.CharField(max_length=20)  
    first_name = models.CharField(max_length=30, blank=True) 
    last_name = models.CharField(max_length=30, blank=True)  
    is_employee = models.BooleanField(default=False) 
    date_joined = models.DateTimeField(auto_now_add=True)  

    class Meta:
        db_table = 'app_users'

    def __str__(self):
        return self.username  # Reprezentacja użytkownika jako jego nazwa użytkownika
    
# Model dla rezerwacji
class Reservation(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE) 
    car = models.ForeignKey(Car, on_delete=models.CASCADE) 
    start_date = models.DateTimeField()  
    end_date = models.DateTimeField()  
    created_at = models.DateTimeField(auto_now_add=True)  
    approved = models.BooleanField(default=False)  

    class Meta:
        db_table = 'app_reservations'

    def __str__(self):
        approval_status = "Zatwierdzona" if self.approved else "Niezatwierdzona"
        return f"Rezerwacja: {self.user} - {self.car} od {self.start_date} do {self.end_date} ({approval_status})"
