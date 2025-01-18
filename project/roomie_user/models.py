# properly/models.py

from django.db import models
from django.contrib.auth.models import User  # Use the default User model
from cloudinary.models import CloudinaryField

class Profile(models.Model):
    PROPERTY_OWNER = 'property_owner'
    HOUSE_SUPERVISOR = 'house_supervisor'
    TENANT = 'tenant'

    USER_ROLES = [
        (PROPERTY_OWNER, 'Property Owner'),
        (HOUSE_SUPERVISOR, 'House Supervisor'),
        (TENANT, 'Tenant'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    bio = models.TextField(blank=True, null=True)
    date_of_birth = models.DateField(null=True, blank=True)
    profile_picture = CloudinaryField('image', blank=True, null=True)
    role = models.CharField(max_length=20, choices=USER_ROLES, default=TENANT)
    roomie_score = models.IntegerField(default=5)  # Add roomie_score with default value 5
    # Add any other custom fields as needed

    def __str__(self):
        return f'{self.user.username} - {self.get_role_display()}'

    def is_property_owner(self):
        return self.role == self.PROPERTY_OWNER

    def is_house_supervisor(self):
        return self.role == self.HOUSE_SUPERVISOR

    def is_tenant(self):
        return self.role == self.TENANT
