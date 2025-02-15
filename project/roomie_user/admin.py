from django.contrib import admin
from django import forms
from .models import CustomUser, AddressHistory
from roomie_property.models import Property
from django.utils import timezone

# Define a custom form for CustomUser
class CustomUserForm(forms.ModelForm):
    class Meta:
        model = CustomUser
        fields = '__all__'

    address = forms.ModelChoiceField(queryset=Property.objects.all(), required=False, empty_label="Select a Property")

    def clean_address(self):
        # If no address is selected, return None (this is valid for a ForeignKey field)
        address = self.cleaned_data.get('address')
        if address is None or address == '':
            return None  # Return None instead of an empty string
        return address

# AddressHistory Inline
class AddressHistoryInline(admin.TabularInline):
    model = AddressHistory
    extra = 0  # No extra empty forms by default
    readonly_fields = ('address', 'start_date', 'end_date')
    fields = ('address', 'start_date', 'end_date')  # Display these fields in the inline

    # Filter AddressHistory to show only for the current user in the admin form
    def get_queryset(self, request):
        qs = super().get_queryset(request)
        if hasattr(self, 'instance') and self.instance:
            # Ensure we are filtering AddressHistory based on the current user instance
            qs = qs.filter(user=self.instance)
        elif 'customuser_id' in request.resolver_match.kwargs:
            # If instance is not available, get the user from the URL
            user_id = request.resolver_match.kwargs['customuser_id']
            qs = qs.filter(user_id=user_id)
        return qs

class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('user', 'address', 'first_name', 'last_name', 'phone_number', 'user_rating_in_app', 'has_address', 'profile_image')
    search_fields = ('user__username', 'first_name', 'last_name', 'email')
    list_filter = ('has_address', 'user_rating_in_app')
    ordering = ('user__username',)

    fieldsets = (
        (None, {
            'fields': ('user', 'first_name', 'last_name', 'email', 'phone_number', 'user_rating_in_app', 'address', 'has_address', 'profile_image')
        }),
    )

    inlines = [AddressHistoryInline]

    def save_model(self, request, obj, form, change):
        # Ensure the address field is properly saved
        if obj.address:
            obj.has_address = True
        else:
            obj.has_address = False

        # Handle address history
        if change:  # Only update address history if updating an existing user
            old_address = CustomUser.objects.get(pk=obj.pk).address
            if obj.address != old_address:
                if old_address:
                    AddressHistory.objects.filter(
                        user=obj, 
                        address=old_address, 
                        end_date__isnull=True
                    ).update(end_date=timezone.now())
                if obj.address:
                    AddressHistory.objects.create(
                        user=obj, 
                        address=obj.address, 
                        start_date=timezone.now()
                    )
        obj.save()

admin.site.register(CustomUser, CustomUserAdmin)
