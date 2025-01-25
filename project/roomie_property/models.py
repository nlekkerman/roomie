from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User

class Property(models.Model):
    # Address-related fields
    street = models.CharField(max_length=255)
    house_number = models.CharField(max_length=20)
    town = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    country = models.CharField(max_length=100)

    # Property-related fields
    property_rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    room_capacity = models.PositiveIntegerField()
    people_capacity = models.PositiveIntegerField()

    # Foreign key to the User model for Owner and Property Supervisor
    owner = models.ForeignKey(User, related_name='owned_properties', on_delete=models.CASCADE)
    property_supervisor = models.ForeignKey(User, related_name='supervised_properties', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"Property {self.house_number} {self.street}, {self.town}, {self.county}, {self.country}"

    def full_address(self):
        """Returns the full address as a string."""
        return f"{self.house_number} {self.street}, {self.town}, {self.county}, {self.country}"

    def save(self, *args, **kwargs):
        # You can add custom save logic here if needed
        super().save(*args, **kwargs)
