from django.contrib import admin
from django import forms
from .models import PropertyCashFlow, RentPayment, UserCashFlow
from django.utils.translation import gettext_lazy as _

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

class RentPaymentAdmin(admin.ModelAdmin):
    list_display = ('property', 'amount', 'date', 'status', 'deadline')
    search_fields = ('property__street', 'property__town', 'status')
    list_filter = ('status',)

    # Read-only fields for 'status' and 'amount' (which will be calculated automatically)
    readonly_fields = ('amount', 'status')

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
class PropertyCashFlowAdmin(admin.ModelAdmin):
    list_display = ('property', 'category', 'amount', 'date', 'status', 'deadline')
    list_filter = ('category', 'status', 'property')
    search_fields = ('property__name', 'category', 'amount')

    def save_model(self, request, obj, form, change):
        """Override save to create UserCashFlow for current tenants when a utility bill is saved."""
        super().save_model(request, obj, form, change)
        # Handle utility bill splitting when saved
        if obj.status == 'paid':
            obj.save()  # Trigger the save to calculate the utility bill split

class UserCashFlowAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'date', 'status', 'deadline')
    list_filter = ('category', 'status', 'user')
    search_fields = ('user__username', 'category', 'amount')

admin.site.register(RentPayment, RentPaymentAdmin)
admin.site.register(PropertyCashFlow, PropertyCashFlowAdmin)
admin.site.register(UserCashFlow, UserCashFlowAdmin)
