from django.db import models
from django.utils.timezone import now


# Create your models here.

# <HINT> Create a Car Make model `class CarMake(models.Model)`:
class CarMake(models.Model):
    make_name = models.CharField(null=False, max_length=100)
    description = models.TextField()
    country = models.CharField(max_length=50)
# - Any other fields you would like to include in car make model
    def __str__(self):
        return "Name: " + self.make_name + "," + \
            "Description: " + self.description + "," + \
            "Country: " + self.country


# <HINT> Create a Car Model model `class CarModel(models.Model):`:
# - Many-To-One relationship to Car Make model (One Car Make has many Car Models, using ForeignKey field)
# - Name
# - Dealer id, used to refer a dealer created in cloudant database
# - Type (CharField with a choices argument to provide limited choices such as Sedan, SUV, WAGON, etc.)
# - Year (DateField)
# - Any other fields you would like to include in car model
# - __str__ method to print a car make object
class CarModel(models.Model):
    SEDAN = 'sedal'
    SUV = 'SUV'
    WAGON = 'wagon'
    TYPES = [
        (SEDAN, 'Sedan'),
        (SUV, 'SUV'),
        (WAGON, "Wagon")
    ]
    dealer_id = models.IntegerField(default=0)
    model_name = models.CharField(null=False, max_length=100)
    car_type = models.CharField(max_length=20, choices=TYPES, default=None)
    year = models.DateField(null=False)
    make = models.ForeignKey(CarMake, on_delete=models.CASCADE)

    def __str__(self):
        return "Name: " + self.model_name + "," + \
            "Car Type: " + self.car_type
            

class CarDealer():
    def __init__(self, name, dealer_id, dealer_address):
        self.name = name
        self.dealer_id = dealer_id
        self.dealer_address = dealer_address


class DealerReview():
    def __init__(self, rev_title, rev_body):
        self.rev_title = rev_title
        self.rev_body = rev_body