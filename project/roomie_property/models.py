from django.db import models

# Create your models here.
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from cloudinary.models import CloudinaryField

class PropertyTenantRecords(models.Model):
    property = models.ForeignKey('Property', related_name='tenant_history', on_delete=models.CASCADE)
    tenant = models.ForeignKey(User, related_name='tenant_history', on_delete=models.CASCADE)
    start_date = models.DateField(default=now)
    end_date = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.tenant.username} ({self.start_date} - {self.end_date or 'Present'})"


class Property(models.Model):
    # Address-related fields
    street = models.CharField(max_length=255)
    house_number = models.CharField(max_length=20)
    town = models.CharField(max_length=100)
    county = models.CharField(max_length=100)
    country = models.CharField(max_length=100)
    folio_number = models.CharField(max_length=50, unique=True, null=True, blank=True)
    air_code = models.CharField(max_length=10, unique=True, null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    property_rating = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)
    room_capacity = models.PositiveIntegerField()
    people_capacity = models.PositiveIntegerField()
    rent_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, default=0.00)

    owner = models.ForeignKey(User, related_name='owned_properties', on_delete=models.CASCADE)
    property_supervisor = models.ForeignKey(User, related_name='supervised_properties', on_delete=models.SET_NULL, null=True, blank=True)

    # Main property image
    main_image = CloudinaryField('main_image', null=True, blank=True)

    # Additional room images
    additional_images = models.ManyToManyField('RoomImage', related_name='properties', blank=True)

    def __str__(self):
        return f"Property {self.house_number} {self.street}, {self.town}, {self.county}, {self.country}"

    def full_address(self):
        """Returns the full address as a string."""
        return f"{self.house_number} {self.street}, {self.town}, {self.county}, {self.country}"
    
    def all_current_tenant(self):
        """Fetch all current tenants."""
        return self.tenant_history.filter(end_date__isnull=True)
    
    def current_tenant(self):
        """Fetch the current tenant."""
        return self.tenant_history.filter(end_date__isnull=True).first()

    def add_tenant(self, tenant, start_date=None):
        """Add a new tenant and end the current tenant's lease."""
        current_tenant = self.current_tenant()
        if current_tenant:
            current_tenant.end_date = start_date or now().date()
            current_tenant.save()

        PropertyTenantRecords.objects.create(
            property=self,
            tenant=tenant,
            start_date=start_date or now().date()
        )

class RoomImage(models.Model):
    # Foreign key to Property
    property = models.ForeignKey(Property, related_name='room_images', on_delete=models.CASCADE)

    image = CloudinaryField('image')
    description = models.CharField(max_length=255)
    
    def __str__(self):
        return self.description or "No description"
