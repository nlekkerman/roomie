from django.db import models
from django.apps import apps
from django.db import models
from django.contrib.auth.models import User
from django.utils.timezone import now
from cloudinary.models import CloudinaryField
from django.dispatch import receiver
from django.db.models.signals import post_save
from django.utils import timezone



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


class TenancyRequest(models.Model):
    tenant = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tenancy_requests")
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name="tenancy_requests")
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name="tenancy_requests_received")
    request_date = models.DateTimeField(default=now)  # Use `now` directly
    status = models.CharField(
        max_length=20,
        choices=[("pending", "Pending"), ("approved", "Approved"), ("rejected", "Rejected")],
        default="pending"
    )
    
    def tenant_first_name(self):
        """Return the first name of the tenant."""
        return self.tenant.first_name

    def tenant_last_name(self):
        """Return the last name of the tenant."""
        return self.tenant.last_name

    def tenant_email(self):
        """Return the email of the tenant."""
        return self.tenant.email

    def tenant_phone(self):
        """Return the phone number of the tenant from the CustomUser model."""
        try:
            return self.tenant.custom_user_profile.phone_number
        except AttributeError:
            return None
    def tenant_rating(self):
        """Return the tenant's rating from their custom user profile."""
        try:
            # Retrieve the custom user profile linked to the tenant (which is a User instance)
            custom_user_profile = self.tenant.custom_user_profile
            return custom_user_profile.user_rating_in_app
        except AttributeError:
            return None
        
    def approve(self):
        """Approve the tenancy request and update tenant's address history."""
        from roomie_user.models import CustomUser, AddressHistory
        from roomie_property.models import PropertyTenantRecords

        # Set status to approved
        self.status = "approved"
        self.save()

        print(f"TenancyRequest {self.id} approved.")

        # Get tenant's CustomUser profile
        try:
            custom_user = self.tenant.custom_user_profile
        except CustomUser.DoesNotExist:
            print(f"CustomUser profile not found for {self.tenant}")
            return  # Exit if the CustomUser profile does not exist

        # Check if the user already has a current address
        if custom_user.address:
            # Set end date for previous address in AddressHistory
            AddressHistory.objects.filter(
                user=custom_user, address=custom_user.address, end_date__isnull=True
            ).update(end_date=timezone.now())

            # Set end date for previous record in PropertyTenantRecords
            PropertyTenantRecords.objects.filter(
                tenant=self.tenant, property=custom_user.address, end_date__isnull=True
            ).update(end_date=timezone.now())

        # Update the user's current address
        custom_user.address = self.property
        custom_user.has_address = True
        custom_user.save()

        # Create new AddressHistory entry
        AddressHistory.objects.create(
            user=custom_user,
            address=self.property,
            start_date=timezone.now(),
        )

        # Create new PropertyTenantRecords entry
        PropertyTenantRecords.objects.create(
            property=self.property,
            tenant=self.tenant,
            start_date=timezone.now(),
        )
        
    def reject(self):
        """Reject the tenancy request."""
        self.status = "rejected"
        self.save()

    def __str__(self):
        return f"Request from {self.tenant.username} to {self.property} - {self.status}"
# Signal to send a notification when a new tenancy request is created

@receiver(post_save, sender=TenancyRequest)
def send_notification_on_request_creation(sender, instance, created, **kwargs):
    """Send notification to property owner when a new tenancy request is created."""
    from communication.models import Notification
    if created:
        message = f"{instance.tenant.first_name} {instance.tenant.last_name} has sent a tenancy request for {instance.property.full_address()}."

        Notification.objects.create(
            sender=instance.tenant,       # Tenant is the sender
            receiver=instance.property.owner,  # Property owner is the receiver
            message=message
        )