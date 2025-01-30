from django.contrib import admin
from django import forms
from .models import PropertyCashFlow, RentPayment, UserCashFlow, TenantBilling,PropertyPayments, PropertyBilling
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from roomie_property.models import Property

class RentPaymentForm(forms.ModelForm):
    class Meta:
        model = RentPayment
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if self.instance and hasattr(self.instance, 'property') and self.instance.property:
            # Automatically set the rent amount from the property model
            self.fields['amount'].initial = self.instance.property.rent_amount  # Assuming `rent_amount` exists on the Property model
        elif not self.instance.pk:
            # If this is a new instance, we cannot access the property yet
            self.fields['amount'].disabled = True  # Disable amount field until property is selected

class TenantBillingInline(admin.TabularInline):
    model = TenantBilling
    extra = 0  # No empty forms by default
    readonly_fields = ('tenant', 'amount', 'status', 'deadline')
    can_delete = False  # Disable deleting tenant billing records
    verbose_name = "Billed Tenant"
    verbose_name_plural = "Billed Tenants"

class RentPaymentAdmin(admin.ModelAdmin):
    list_display = (
        'property','get_property_owner', 'amount', 'date', 'status', 'deadline', 'get_billed_tenants', 'get_billed_amount'
    )
    search_fields = ('property__street', 'property__town', 'status')
    list_filter = ('status',)

    # Read-only fields for 'status' and 'amount' (which will be calculated automatically)
    readonly_fields = ('get_property_owner','amount', 'status')  # Make billed_tenants read-only, no longer needed in RentPayment model

    # Inline for TenantBilling
    inlines = [TenantBillingInline]

    def get_billed_tenants(self, obj):
        """Custom method to display billed tenants in the admin list view."""
        billed_tenants = obj.tenant_billings.all()
        if billed_tenants:
            return ', '.join([billing.tenant.username for billing in billed_tenants])
        return 'No tenants billed'
    get_billed_tenants.short_description = 'Billed Tenants'

    def get_billed_amount(self, obj):
        """Custom method to display the total billed amount in the admin list view."""
        billed_tenants = obj.tenant_billings.all()
        total_billed = sum([billing.amount for billing in billed_tenants])
        return total_billed
    get_billed_amount.short_description = 'Total Billed Amount'

    def get_property_owner(self, obj):
        """Custom method to display the property owner in the admin list view."""
        if obj.property and hasattr(obj.property, 'owner'):
            return obj.property.owner.username  # Assuming the owner is a User model with a 'username' field
        return 'No owner'
    get_property_owner.short_description = 'Property Owner'

    def get_form(self, request, obj=None, **kwargs):
        """Override get_form to automatically populate the 'amount' field in the admin."""
        form = super().get_form(request, obj, **kwargs)
        if obj is None:  # Only populate the amount if it's a new RentPayment
            property = form.base_fields['property'].initial
            if property:
                property_instance = form.base_fields['property'].queryset.get(id=property)
                form.base_fields['amount'].initial = property_instance.rent_amount
        return form

    def save_model(self, request, obj, form, change):
        """Override save_model to automatically handle rent calculation and tenant billing."""
        if not obj.amount:
            obj.amount = obj.property.rent_amount  # Use rent_amount from the property if not provided

        # Call the save method to create the RentPayment and split the rent
        super().save_model(request, obj, form, change)

        # Fetch all current tenants for this property (those with no end_date)
        current_tenants = obj.property.tenant_history.filter(end_date__isnull=True)

        if current_tenants:
            split_amount = obj.amount / current_tenants.count()  # Split the rent equally among tenants
            description = f"Rent payment for property {obj.property.id}"

            # Create UserCashFlow entries for each tenant and corresponding TenantBilling entries
            for tenant_record in current_tenants:
                user = tenant_record.tenant  # Access the tenant (User instance)
                if user:
                    # Check if TenantBilling already exists for this RentPayment and tenant
                    if not TenantBilling.objects.filter(rent_payment=obj, tenant=user).exists():
                        # Create a UserCashFlow entry
                        UserCashFlow.objects.create(
                            user=user,
                            amount=split_amount,
                            date=obj.date,
                            description=description,
                            category='rent',
                            status='pending',
                            deadline=obj.deadline or timezone.now().date() + timezone.timedelta(days=30),
                        )

                        # Create a TenantBilling entry for each tenant if it doesn't exist
                        TenantBilling.objects.create(
                            rent_payment=obj,
                            tenant=user,
                            amount=split_amount,
                            status='pending',
                            deadline=obj.deadline or timezone.now().date() + timezone.timedelta(days=30),
                        )

        # After saving the RentPayment, update the status based on TenantBilling
        obj.update_status_if_paid()
          
class UserCashFlowAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'date', 'status', 'deadline')
    list_filter = ('category', 'status', 'user')
    readonly_fields = ('user', 'category', 'amount', 'date', 'deadline', 'description')


    def save_model(self, request, obj, form, change):
        """Custom save logic for admin to handle RentPayment and TenantBilling updates."""
        # Call the save method on the UserCashFlow instance
        super().save_model(request, obj, form, change)

        # If the status has been updated to 'paid' and the category is 'rent', update RentPayment and TenantBilling status
        if obj.status == 'paid' and obj.category == 'rent':
            # Update RentPayment and TenantBilling statuses as done in the model's save method
            rent_payments = RentPayment.objects.filter(
                property__tenant_history__tenant=obj.user,
                status='pending'
            )
            for rent_payment in rent_payments:
                # Check if all tenants have paid for this rent payment
                all_paid = True
                for tenant_billing in rent_payment.tenant_billings.all():
                    if tenant_billing.status != 'paid':
                        all_paid = False
                        break

                # If all tenants have paid, update the RentPayment status to 'paid'
                if all_paid:
                    rent_payment.status = 'paid'
                    rent_payment.save()

# Inline for PropertyBilling
class PropertyBillingInline(admin.TabularInline):  # Or admin.StackedInline for a different layout
    model = PropertyBilling
    extra = 0  # Number of empty forms to display by default
    fields = ['tenant', 'amount', 'status', 'deadline', 'category']  # You can adjust the fields as needed
    readonly_fields = ['tenant', 'amount', 'status', 'deadline', 'category']
   

    def save_model(self, request, obj, form, change):
        """Custom save logic for PropertyCashFlow."""
        super().save_model(request, obj, form, change)
# Admin for PropertyPayments
class PropertyPaymentsAdmin(admin.ModelAdmin):
    list_display = ('property', 'category', 'amount', 'date', 'status', 'deadline')
    list_filter = ('category', 'status', 'property')
    search_fields = ('property__name', 'category',)
    inlines = [PropertyBillingInline]  # Add PropertyBilling as an inline
    
    
    
    def get_property_owner(self, obj):
            """Custom method to display the property owner in the admin list view."""
            if obj.property and hasattr(obj.property, 'owner'):
                return obj.property.owner.username  # Assuming the owner is a User model with a 'username' field
            return 'No owner'
    get_property_owner.short_description = 'Property Owner'                    

admin.site.register(PropertyPayments, PropertyPaymentsAdmin)
admin.site.register(RentPayment, RentPaymentAdmin)
admin.site.register(UserCashFlow, UserCashFlowAdmin)
