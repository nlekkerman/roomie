from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

import logging

logger = logging.getLogger(__name__)

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
    to_pay_order = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.category} - {self.amount} ({self.date})"

    def save(self, *args, **kwargs):
        """Update the status to 'paid' if to_pay_order is True, and update RentPayment and TenantBilling status accordingly."""
        
        # Log the initial state before saving
        logger.info(f"Saving UserCashFlow instance: {self.user.username} - {self.category} - {self.amount} - Status: {self.status} - To Pay Order: {self.to_pay_order}")
        
        if self.to_pay_order and self.status != 'paid':
            self.status = 'paid'
            logger.info(f"Updated status to 'paid' for UserCashFlow instance: {self.user.username} - {self.category} - {self.amount}")
        
        # Save the UserCashFlow instance
        super().save(*args, **kwargs)

        # Log after saving
        logger.info(f"Saved UserCashFlow instance: {self.user.username} - {self.category} - {self.amount} - Status: {self.status} - To Pay Order: {self.to_pay_order}")

        # If the category is 'rent' and status is updated to 'paid', update RentPayment status and related TenantBilling entries
        if self.category == 'rent' and self.status == 'paid':
            # Fetch the RentPayment entries associated with this user
            rent_payments = RentPayment.objects.filter(property__tenant_history__tenant=self.user, status='pending')

            # Log rent payment update
            logger.info(f"Checking RentPayment for User: {self.user.username} - Rent Payments found: {rent_payments.count()}")

            for rent_payment in rent_payments:
                # Log RentPayment details for debugging
                logger.info(f"Processing RentPayment ID: {rent_payment.id} for User: {self.user.username}")

                # Check if all tenants have paid for this rent payment
                all_paid = True
                for tenant_billing in rent_payment.tenant_billings.filter(tenant=self.user):
                    logger.info(f"Checking TenantBilling ID: {tenant_billing.id} for User: {self.user.username} - Status: {tenant_billing.status}")
                    if tenant_billing.status != 'paid':
                        tenant_billing.status = 'paid'
                        tenant_billing.save()  # Save the updated TenantBilling
                        logger.info(f"Updated TenantBilling ID: {tenant_billing.id} status to 'paid' for User: {self.user.username}")
                        all_paid = False
                        break

                # If all tenants have paid, update the RentPayment status to 'paid'
                if all_paid:
                    rent_payment.status = 'paid'
                    rent_payment.save()

                    # Log RentPayment status update
                    logger.info(f"Updated RentPayment status to 'paid' for RentPayment ID: {rent_payment.id}")

                    # Update TenantBilling status for the corresponding rent payment
                    tenant_billing = rent_payment.tenant_billings.filter(tenant=self.user, status='pending').first()
                    if tenant_billing:
                        tenant_billing.status = 'paid'
                        tenant_billing.save()
                        
                        # Log TenantBilling status update
                        logger.info(f"Updated TenantBilling status to 'paid' for TenantBilling ID: {tenant_billing.id}")
            
        if self.status == 'paid':
                # Fetch the PropertyBilling entries associated with this user and category
                property_billings = PropertyBilling.objects.filter(
                    tenant=self.user,
                    property_payment__category=self.category,  # Match the category from PropertyPayment
                    status='pending'
                )

                # Log the count of PropertyBilling entries found
                property_billing_count = property_billings.count()
                logger.info(f"Checking PropertyBilling for User: {self.user.username} - Found {property_billing_count} pending Property Billings.")

                if property_billing_count == 0:
                    logger.warning(f"No pending PropertyBilling entries found for User: {self.user.username} in category: {self.category}.")
                    return  # Exit if no PropertyBilling entries are found

                # Initialize a variable to track if all property billings are paid
                all_property_billings_paid = True

                # Process each PropertyBilling entry
                for property_billing in property_billings:
                    # Check if property_payment exists (it might be None if the field is nullable)
                    if property_billing.property_payment:
                        logger.info(f"Processing PropertyBilling ID: {property_billing.id} for User: {self.user.username}")

                        # Update the PropertyBilling status to 'paid'
                        property_billing.status = 'paid'
                        property_billing.save()
                        logger.info(f"Updated PropertyBilling ID: {property_billing.id} status to 'paid' for User: {self.user.username}")

                        # Check if any PropertyBilling remains unpaid
                        if property_billing.status != 'paid':
                            all_property_billings_paid = False
                    else:
                        # Log a warning if property_payment is None
                        logger.warning(f"PropertyBilling ID: {property_billing.id} has no associated PropertyPayment. Skipping update.")

                # After processing all PropertyBillings, check if all are paid
                if all_property_billings_paid:
                    logger.info(f"All PropertyBilling entries for User: {self.user.username} in category: {self.category} have been marked as 'paid'.")
                else:
                    logger.warning(f"Some PropertyBilling entries for User: {self.user.username} in category: {self.category} remain unpaid.")


    
    @property
    def first_name(self):
        return self.user.first_name

    @property
    def last_name(self):
        return self.user.last_name

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
        """Save the PropertyCashFlow instance without directly creating payments."""
        
        # Log the initial state before saving
        logger.info(f"Saving PropertyCashFlow instance: Property ID: {self.property.id} - {self.category} - {self.amount} - Status: {self.status}")
        
        # Save the PropertyCashFlow instance first
        super().save(*args, **kwargs)

        # Log after saving
        logger.info(f"Saved PropertyCashFlow instance: Property ID: {self.property.id} - {self.category} - {self.amount} - Status: {self.status}")

               

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
        """Automatically calculate rent and split it among tenants, avoiding duplicate billing."""
        if not self.amount:
            self.amount = self.property.rent_amount  # Use the rent amount from the Property model if not provided

        super().save(*args, **kwargs)  # Save the RentPayment instance

        # Fetch all current tenants for this property (those with no end_date)
        current_tenants = self.property.tenant_history.filter(end_date__isnull=True)

        if current_tenants:
            split_amount = self.amount / current_tenants.count()  # Split the rent equally among tenants
            description = f"Rent payment for property {self.property.id}"

            # Create UserCashFlow entries for each tenant and corresponding TenantBilling entries
            for tenant_record in current_tenants:
                user = tenant_record.tenant  # Access the tenant (User instance)
                if user:
                    # Check if TenantBilling already exists for this RentPayment and tenant
                    if not TenantBilling.objects.filter(rent_payment=self, tenant=user).exists():
                        # Create a UserCashFlow entry
                        UserCashFlow.objects.create(
                            user=user,
                            amount=split_amount,
                            date=self.date,
                            description=description,
                            category='rent',
                            status='pending',
                            deadline=self.deadline or timezone.now().date() + timezone.timedelta(days=30),
                        )

                        # Create a TenantBilling entry for each tenant if it doesn't exist
                        TenantBilling.objects.create(
                            rent_payment=self,
                            tenant=user,
                            amount=split_amount,
                            status='pending',
                            deadline=self.deadline or timezone.now().date() + timezone.timedelta(days=30),
                        )

    def update_status_if_paid(self):
        """Update the RentPayment status to 'paid' if all tenants have paid."""
        all_paid = True
        # Check if all tenants have paid (based on TenantBilling status)
        for tenant_billing in self.tenant_billings.all():
            if tenant_billing.status != 'paid':
                all_paid = False
                break

        # If all tenants have paid, update the RentPayment status to 'paid'
        if all_paid:
            self.status = 'paid'
            self.save(update_fields=['status'])

class TenantBilling(models.Model):
    rent_payment = models.ForeignKey('RentPayment', related_name='tenant_billings', on_delete=models.CASCADE)
    tenant = models.ForeignKey('auth.User', on_delete=models.CASCADE)  # Assuming tenant is a User
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('paid', 'Paid'), ('pending', 'Pending')])
    deadline = models.DateField()

    def __str__(self):
        return f"Tenant {self.tenant.username} - {self.amount} ({self.status})"

    
class PropertyPayments(models.Model):
    PROPERTY_PAYMENT_CHOICES = [
        ('electricity', 'Electricity'),
        ('garbage', 'Garbage'),
        ('internet', 'Internet'),
        ('heating', 'Heating'),
    ]
    STATUS_CHOICES = [
        ('paid', 'Paid'),
        ('pending', 'Pending'),
    ]

    property = models.ForeignKey('roomie_property.Property', on_delete=models.CASCADE, related_name='property_utility_payments')
    category = models.CharField(max_length=50, choices=PROPERTY_PAYMENT_CHOICES, default='category')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(default=timezone.now)
    description = models.CharField(max_length=255, default="Property payment")
    status = models.CharField(max_length=50, choices=STATUS_CHOICES, default='pending')
    deadline = models.DateField(null=True, blank=True)

    def __str__(self):
        return f"Payment for {self.property.id} - {self.category} - {self.amount} ({self.date})"

    def save(self, *args, **kwargs):
        """Automatically calculate and split payments among tenants, create UserCashFlow, PropertyBilling, and PropertyPayments if needed."""
        is_new_instance = self.pk is None
        super().save(*args, **kwargs)  # Save the PropertyPayments instance first

        if is_new_instance and self.status == 'pending':
            # Fetch all current tenants for this property (those with no end_date)
            current_tenants = self.property.tenant_history.filter(end_date__isnull=True)

            if current_tenants.exists():
                split_amount = self.amount / current_tenants.count()  # Split payment equally among tenants
                description = f"{self.category.capitalize()} payment for property {self.property.id}"

                # Ensure a PropertyPayments entry exists for the property and category
                property_payment = PropertyPayments.objects.filter(property=self.property, category=self.category, status='pending').first()
                if not property_payment:
                    property_payment = PropertyPayments.objects.create(
                        property=self.property,
                        category=self.category,
                        amount=self.amount,
                        date=self.date,
                        description=self.description,
                        status='pending',
                        deadline=self.deadline or timezone.now().date() + timezone.timedelta(days=30)
                    )

                # Create UserCashFlow and PropertyBilling entries for each tenant
                for tenant_record in current_tenants:
                    tenant = tenant_record.tenant
                    if tenant:
                        # Check if PropertyBilling already exists for this PropertyPayments and tenant
                        if not PropertyBilling.objects.filter(property_payment=property_payment, tenant=tenant).exists():
                            # Create a UserCashFlow entry
                            UserCashFlow.objects.create(
                                user=tenant,
                                amount=split_amount,
                                date=self.date,
                                description=description,
                                category=self.category,
                                status='pending',
                                deadline=self.deadline or timezone.now().date() + timezone.timedelta(days=30),
                            )

                            # Create a PropertyBilling entry for the tenant with the category
                            PropertyBilling.objects.create(
                                property_payment=property_payment,
                                tenant=tenant,
                                amount=split_amount,
                                status='pending',
                                deadline=self.deadline or timezone.now().date() + timezone.timedelta(days=30),
                                category=self.category  # Set the category from PropertyPayments
                            )
                

    def update_status_if_paid(self):
        """Update the PropertyPayments status to 'paid' if all related PropertyBilling entries are marked as 'paid'."""
        all_paid = not self.propertybilling_set.exclude(status='paid').exists()

        if all_paid:
            self.status = 'paid'
            self.save(update_fields=['status'])

class PropertyBilling(models.Model):
    property_payment = models.ForeignKey(PropertyPayments, related_name='property_billings', on_delete=models.CASCADE, null=True, blank=True)
    tenant = models.ForeignKey(User, related_name='tenant_bills', on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=50, choices=[('paid', 'Paid'), ('pending', 'Pending')], default='pending')
    deadline = models.DateField(null=True, blank=True)
    category = models.CharField(max_length=50, choices=PropertyPayments.PROPERTY_PAYMENT_CHOICES, default='electricity')
    
    def __str__(self):
        return f"Billing for {self.tenant.username} - {self.amount} ({self.status}) - Category: {self.category}"

