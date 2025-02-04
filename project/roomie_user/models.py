from django.db import models
from roomie_property.models import Property, PropertyTenantRecords
from django.utils import timezone
from django.contrib.auth.models import User
from cloudinary.models import CloudinaryField

class AddressHistory(models.Model):
    user = models.ForeignKey('CustomUser', on_delete=models.CASCADE, related_name='address_history')
    address = models.ForeignKey(Property, on_delete=models.SET_NULL, null=True, blank=True)
    start_date = models.DateTimeField(default=timezone.now)
    end_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        # Safely access user and address, ensuring no errors if they are None
       
        user_str = self.user.email if self.user and self.user.email else "Unknown User"
        address_str = self.address.full_address() if self.address else "No Address"
        start_date_str = self.start_date.strftime('%Y-%m-%d') if self.start_date else "Unknown Start Date"
        end_date_str = self.end_date.strftime('%Y-%m-%d') if self.end_date else "Present"  # If no end date, show "Present"
    
        return f"Address history for {user_str} at {address_str} from {start_date_str} to {end_date_str}"

    class Meta:
        ordering = ['-start_date']  # Order by start_date in descending order


class CustomUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='custom_user_profile')
    user_rating_in_app = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)  # User's rating in the app
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.ForeignKey('roomie_property.Property', on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    has_address = models.BooleanField(default=False)
    profile_image = CloudinaryField('image', blank=True, null=True)
   
    def __str__(self):
        # Access the username of the related User model
       return self.user.email if self.user and self.user.email else "Unknown User"

    def save(self, *args, **kwargs):
        """Ensure the User exists before saving and update tenant records when address changes."""
        
        # Ensure the user is assigned before saving
        if not self.user_id:
            raise ValueError("Cannot save CustomUser without a linked User instance.")
        is_new = self._state.adding  # Check if this is a new object (creation)
        old_address = None  

        if not is_new:  # If updating an existing user
            old_user = CustomUser.objects.get(pk=self.pk)
            old_address = old_user.address  # Get previous address

        super().save(*args, **kwargs)  # ✅ First, save the CustomUser

        if is_new or self.address != old_address:  # Only proceed if new or address changed
            if old_address:  # If address changed, close previous address history
                AddressHistory.objects.filter(
                    user=self, 
                    address=old_address, 
                    end_date__isnull=True
                ).update(end_date=timezone.now())

                PropertyTenantRecords.objects.filter(
                    tenant=self.user,
                    property=old_address,
                    end_date__isnull=True
                ).update(end_date=timezone.now())

            if self.address:  # ✅ Now safe to create new address history
                AddressHistory.objects.create(
                    user=self, 
                    address=self.address, 
                    start_date=timezone.now()
                )
                PropertyTenantRecords.objects.create(
                    tenant=self.user,
                    property=self.address,
                    start_date=timezone.now()
                )

        # Populate missing fields from User
        if not self.first_name:
            self.first_name = self.user.first_name or "Default First Name"
        if not self.last_name:
            self.last_name = self.user.last_name or "Default Last Name"
        if not self.email:
            self.email = self.user.email or "default@example.com"
        if not self.phone_number:
            self.phone_number = self.user.profile.phone_number if hasattr(self.user, 'profile') else ""

        # Handle address field
        if self.address is None:  
            self.address = self.user.profile.address if hasattr(self.user, 'profile') else None

        # Set has_address based on whether an address is present
        self.has_address = bool(self.address)

        # Ensure profile image is correctly saved
        if not hasattr(self, "profile_image") or not self.profile_image:
            self.profile_image = None  # Set default if no image is provided

        # Ensure user rating has a default
        if not self.user_rating_in_app:
            self.user_rating_in_app = 5.0  

        super().save(*args, **kwargs)
