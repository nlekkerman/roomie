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
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='custom_user_profile')
    user_rating_in_app = models.DecimalField(max_digits=3, decimal_places=1, default=5.0)  # User's rating in the app
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.ForeignKey('roomie_property.Property', on_delete=models.SET_NULL, null=True, blank=True)
    first_name = models.CharField(max_length=30, blank=True, null=True)
    last_name = models.CharField(max_length=30, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    has_address = models.BooleanField(default=False)
    profile_image = CloudinaryField('image', blank=True, null=True)
    is_owner = models.BooleanField(default=False)

    def __str__(self):
        return self.user.email if self.user and self.user.email else "Unknown User"

    def save(self, *args, **kwargs):
        """Ensure that tenant records are updated correctly when the address changes."""
        
        if not self.user_id:
            raise ValueError("Cannot save CustomUser without a linked User instance.")

        is_new = self._state.adding  # Check if this is a new object
        old_address = None

        if not is_new:  
            old_user = CustomUser.objects.get(pk=self.pk)
            old_address = old_user.address  # Get the previous address

        super().save(*args, **kwargs)  # Save the CustomUser first

        if self.address and (is_new or self.address != old_address):  
            if old_address:  
                # ✅ Close previous address history and set end_date
                AddressHistory.objects.filter(
                    user=self, 
                    address=old_address, 
                    end_date__isnull=True
                ).update(end_date=timezone.now())  # Close old address history

                # ✅ Close previous tenancy records and set end_date
                PropertyTenantRecords.objects.filter(
                    tenant=self.user,
                    property=old_address,
                    end_date__isnull=True
                ).update(end_date=timezone.now())  # Close old tenancy records

            # ✅ Prevent duplicate active records
            existing_record = PropertyTenantRecords.objects.filter(
                tenant=self.user,
                property=self.address,
                end_date__isnull=True
            ).exists()

            if not existing_record:  
                PropertyTenantRecords.objects.create(
                    tenant=self.user,
                    property=self.address,
                    start_date=timezone.now()  # Create new record with start date
                )

        self.has_address = bool(self.address)

        super().save(*args, **kwargs)

