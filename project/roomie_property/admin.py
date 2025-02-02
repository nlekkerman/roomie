from django.contrib import admin
from django.utils.html import format_html
from .models import Property, PropertyTenantRecords, RoomImage

class PropertyTenantHistoryInline(admin.TabularInline):
    model = PropertyTenantRecords
    extra = 0  # No extra empty forms by default
    readonly_fields = ('tenant', 'start_date', 'end_date')  # Make tenant history read-only in the property admin
    can_delete = False  # Prevent deletion from inline (optional)

class RoomImageInline(admin.TabularInline):
    model = RoomImage
    extra = 1  # Number of empty forms initially

class PropertyAdmin(admin.ModelAdmin):
    list_display = ('full_address_display', 'main_image_display','owner',
                    'property_rating', 'room_capacity', 'people_capacity', 
                    'property_supervisor', 'rent_amount', 'deposit_amount', 'current_tenants_display')
    
    search_fields = ('street', 'town', 'county', 'country', 
                     'owner__username', 'property_supervisor__username')

    inlines = [RoomImageInline,PropertyTenantHistoryInline]  # Add the inline for room images

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
                'street', 'house_number', 'town', 'county', 'country', 'main_image',
                'property_rating', 'room_capacity', 'rent_amount', 'people_capacity', 'deposit_amount',
                'owner', 'property_supervisor'
            )
        else:  # When adding a new Property
            fieldsets[0][1]['fields'] = (
                'street', 'house_number', 'town', 'county', 'country', 'main_image',
                'property_rating', 'room_capacity', 'people_capacity', 'rent_amount','deposit_amount',
                'owner', 'property_supervisor'
            )
        return fieldsets
# Register Property with the admin interface
admin.site.register(Property, PropertyAdmin)
