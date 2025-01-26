from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class UserCashFlow(models.Model):
    CATEGORY_CHOICES = [
        ('rent', 'Rent'),
        ('electricity', 'Electricity'),
        ('garbage', 'Garbage'),
        ('internet', 'Internet'),
        ('heating', 'Heating'),
    ]
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
    ]

    user = models.ForeignKey(User, related_name='cash_flow', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.amount} ({self.date})"

class PropertyCashFlow(models.Model):
    CATEGORY_CHOICES = [
        ('electricity', 'Electricity'),
        ('garbage', 'Garbage'),
        ('internet', 'Internet'),
        ('heating', 'Heating'),
    ]
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
    ]

    property = models.ForeignKey('roomie_property.Property', related_name='cash_flows', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Optional for utility bills
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255)
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)  # Rent excluded here
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Property {self.property.id} - {self.category} - {self.amount} ({self.date})"

    def save(self, *args, **kwargs):
        """Override save to create UserCashFlow for current tenants."""
        is_new_instance = self.pk is None
        super().save(*args, **kwargs)  # Save the PropertyCashFlow instance first

        if is_new_instance:
            # Use the current_tenant array to find active tenants
            current_tenants = self.property.current_tenant  # Assuming this is a list of user IDs

            if current_tenants:
                # For utility bills, split the amount among tenants
                split_amount = self.amount / len(current_tenants)
                description = f"{self.category} bill for property {self.property.id}"

                # Create UserCashFlow entries for each tenant
                for tenant_id in current_tenants:
                    user = User.objects.get(id=tenant_id)
                    UserCashFlow.objects.create(
                        user=user,
                        amount=split_amount,
                        date=self.date,
                        description=description,
                        category=self.category,
                        status='pending',
                        deadline=self.deadline or timezone.now().date() + timezone.timedelta(days=30),
                    )

    def send_electricity_bill(self, amount):
        """Manually enter the amount for electricity bill and split it among tenants."""
        self.category = 'electricity'
        self.amount = amount
        self.save()

    def send_other_bill(self, category, amount):
        """Manually enter the amount for any other bill and split it among tenants."""
        self.category = category
        self.amount = amount
        self.save()
        
class RentPayment(models.Model):
    property = models.ForeignKey('roomie_property.Property', related_name='rent_payments', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)  # Rent amount
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255, default="Rent payment")
    status = models.CharField(max_length=50, choices=[('paid', 'Paid'), ('pending', 'Pending')], default='pending')
    deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Rent payment for property {self.property.id} - {self.amount} ({self.date})"

    def save(self, *args, **kwargs):
        """Automatically calculate rent and split it among tenants."""
        if not self.amount:
            self.amount = self.property.rent_amount  # Use the rent amount from the Property model if not provided

        super().save(*args, **kwargs)  # Save the RentPayment instance

        # Fetch all current tenants for this property (those with no end_date)
        current_tenants = self.property.tenant_history.filter(end_date__isnull=True)

        if current_tenants:
            split_amount = self.amount / current_tenants.count()  # Split the rent equally among tenants
            description = f"Rent payment for property {self.property.id}"

            # Create UserCashFlow entries for each tenant
            for tenant_record in current_tenants:
                # Access the 'tenant' field which is a ForeignKey to the User model
                user = tenant_record.tenant  # This references the User model
                if user:
                    UserCashFlow.objects.create(
                        user=user,
                        amount=split_amount,
                        date=self.date,
                        description=description,
                        category='rent',
                        status='pending',
                        deadline=self.deadline or timezone.now().date() + timezone.timedelta(days=30),
                    )
             
