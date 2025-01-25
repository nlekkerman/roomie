from django.db import models
from roomie_property.models import Property
from django.utils import timezone
from django.contrib.auth.models import User

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

    def __str__(self):
        # Access the username of the related User model
       return self.user.email if self.user and self.user.email else "Unknown User"

    def save(self, *args, **kwargs):
        if self.pk:  # Only do this when updating an existing user
            old_user = CustomUser.objects.get(pk=self.pk)
            old_address = old_user.address  # Ensure this is a Property instance

            # If the address is changed, record the old address with an end date
            if self.address != old_address:
                if old_address:  # Only save history if the old address exists
                    # Save old address with end date (current time)
                    AddressHistory.objects.filter(
                        user=self, 
                        address=old_address, 
                        end_date__isnull=True
                    ).update(end_date=timezone.now())

                # Add new address to address history
                if self.address:
                    AddressHistory.objects.create(
                        user=self, 
                        address=self.address, 
                        start_date=timezone.now()
                    )

        # Populate fields from User model if CustomUser is being created or updated
        if not self.first_name and self.user:
            self.first_name = self.user.first_name or 'Default First Name'
        if not self.last_name and self.user:
            self.last_name = self.user.last_name or 'Default Last Name'
        if not self.email and self.user:
            self.email = self.user.email or 'default@example.com'

        if not self.phone_number and self.user:
            self.phone_number = self.user.profile.phone_number if hasattr(self.user, 'profile') else ''

        # Handle address field
        if self.address is None:  # Only set address from user profile if it's not set in the form
            if hasattr(self.user, 'profile') and self.user.profile.address:
                self.address = self.user.profile.address
            else:
                self.address = None  # Set to None, not an empty string

        # Set has_address based on whether address is populated
        self.has_address = bool(self.address)

        if not self.user_rating_in_app:
            self.user_rating_in_app = 5.0  # Default value if not set

        super().save(*args, **kwargs)
