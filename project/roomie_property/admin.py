from django.contrib import admin
from django.utils.html import format_html
from .models import Property, PropertyTenantRecords, RoomImage, TenancyRequest
from roomie_user.models import CustomUser  
from communication.models import Notification
from django.utils.timezone import now

class PropertyTenantHistoryInline(admin.TabularInline):
    model = PropertyTenantRecords
    extra = 0  # No extra empty forms by default
    readonly_fields = ('tenant', 'start_date', 'end_date')  # Make tenant history read-only in the property admin
    can_delete = False  # Prevent deletion from inline (optional)


class TenancyRequestInline(admin.TabularInline):
    model = TenancyRequest
    extra = 0  # No empty form initially
    fields = ('tenant', 'status', 'request_date')  # Display only relevant fields
    readonly_fields = ('tenant', 'request_date')  # Make fields read-only to prevent changes

    def get_queryset(self, request):
        """Show only pending tenancy requests and remove others from admin panel."""
        queryset = super().get_queryset(request)
        return queryset.filter(status='pending')  # Only include pending requests

    def tenant_display(self, obj):
        return obj.tenant.username if obj.tenant else "No tenant"

    tenant_display.short_description = 'Tenant'

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1  # Number of empty forms initially

class PropertyAdmin(admin.ModelAdmin):
    list_display = ('full_address_display','air_code', 'description', 'main_image_display', 'owner', 'folio_number',
                    'property_rating', 'room_capacity', 'people_capacity', 
                    'property_supervisor', 'rent_amount', 'deposit_amount', 'current_tenants_display')
    
    search_fields = ('street', 'town', 'county', 'country', 
                     'owner__username', 'property_supervisor__username')

    inlines = [RoomImageInline, PropertyTenantHistoryInline, TenancyRequestInline]
    
    
    
    # 🔹 **Display full address**
    def full_address_display(self, obj):
        return obj.full_address()  # Calls the `full_address()` method from the model
    
    full_address_display.short_description = "Address"

    # 🔹 **Display main image in the admin list view**
    def main_image_display(self, obj):
        if obj.main_image:
            return format_html('<img src="{}" style="width: 50px; height: 50px; object-fit: cover;" />', obj.main_image.url)
        return "No image"
    
    main_image_display.short_description = 'Main Image'
    
    # 🔹 **Display current tenants in the admin list view**
    def current_tenants_display(self, obj):
        current_tenants = obj.tenant_history.filter(end_date__isnull=True)
        tenants_list = ", ".join([tenant.tenant.username for tenant in current_tenants])
        return format_html(f"<strong>{tenants_list}</strong>") if tenants_list else "No current tenants"

    current_tenants_display.short_description = "Current Tenants"

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # If editing an existing Property
            fieldsets[0][1]['fields'] = (
                'street', 'house_number', 'town', 'county', 'country', 'folio_number', 'main_image',
                'property_rating', 'room_capacity', 'rent_amount', 'people_capacity', 'deposit_amount',
                'owner', 'property_supervisor', 'description'
            )
        else:  # When adding a new Property
            fieldsets[0][1]['fields'] = (
                'street', 'house_number', 'town', 'county', 'country', 'air_code', 'folio_number', 'description', 'main_image',
                'property_rating', 'room_capacity', 'people_capacity', 'rent_amount','deposit_amount',
                'owner', 'property_supervisor'
            )
        return fieldsets
    

class TenancyRequestAdmin(admin.ModelAdmin):
    list_display = ('tenant', 'property_display', 'owner_display', 'status', 'request_date')
    list_editable = ('status',)

    # Display the property full address in the admin list view
    def property_display(self, obj):
        return obj.property.full_address() if obj.property else "No property"

    property_display.short_description = 'Property'

    # Display the tenant's username in the admin list view
    def tenant_display(self, obj):
        return obj.tenant.username if obj.tenant else "No tenant"

    tenant_display.short_description = 'Tenant'

    # Display the owner's username in the admin list view
    def owner_display(self, obj):
        return obj.owner.username if obj.owner else "No owner"

    owner_display.short_description = 'Owner'

    # Make sure the status field is a dropdown for selecting status
    def get_list_display_links(self, request, list_display):
        return ('tenant',)

    # Read-only fields for displaying user information
    def tenant_first_name(self, obj):
        return obj.tenant.first_name if obj.tenant else "N/A"

    tenant_first_name.short_description = "Tenant's First Name"

    def tenant_last_name(self, obj):
        return obj.tenant.last_name if obj.tenant else "N/A"

    tenant_last_name.short_description = "Tenant's Last Name"

    def tenant_email(self, obj):
        return obj.tenant.email if obj.tenant else "N/A"

    tenant_email.short_description = "Tenant's Email"

    def tenant_phone_number(self, obj):
        custom_user = CustomUser.objects.get(user=obj.tenant) if obj.tenant else None
        return custom_user.phone_number if custom_user else "N/A"

    tenant_phone_number.short_description = "Tenant's Phone Number"

    def tenant_rating(self, obj):
        custom_user = CustomUser.objects.get(user=obj.tenant) if obj.tenant else None
        return custom_user.user_rating_in_app if custom_user else "N/A"

    tenant_rating.short_description = "Tenant's Rating"

    # List of read-only fields for the form
    readonly_fields = ('owner','tenant','tenant_first_name', 'tenant_last_name', 'tenant_email', 'tenant_phone_number', 'tenant_rating')

    # Overriding save_model to handle the approval logic
    def save_model(self, request, obj, form, change):
        # Send a notification to the property owner
        if obj.property and obj.property.owner:
            owner = obj.property.owner
            notification_message = (
                f"New tenancy request from {obj.tenant.first_name} {obj.tenant.last_name} "
                f"for your property at {obj.property.full_address()}."
            )
            Notification.objects.create(
                user=owner,  # Notify the property owner
                message=notification_message,
                created_at=now
            )

           
            
            
        super().save_model(request, obj, form, change)

admin.site.register(TenancyRequest, TenancyRequestAdmin)

# Register Property with the admin interface
admin.site.register(Property, PropertyAdmin)
