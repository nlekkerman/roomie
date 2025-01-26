from django.contrib import admin
from django.utils.html import format_html
from .models import Property, PropertyTenantRecords

class PropertyTenantHistoryInline(admin.TabularInline):
    model = PropertyTenantRecords
    extra = 0  # No extra empty forms by default
    readonly_fields = ('tenant', 'start_date', 'end_date')  # Make tenant history read-only in the property admin
    can_delete = False  # Prevent deletion from inline (optional)

class PropertyAdmin(admin.ModelAdmin):
    list_display = ('street', 'house_number', 'town', 'county', 'country', 
                    'property_rating', 'room_capacity', 'people_capacity', 
                    'owner', 'property_supervisor', 'current_tenants_display')
    search_fields = ('street', 'town', 'county', 'country', 
                     'owner__username', 'property_supervisor__username')

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # If editing an existing Property
            fieldsets[0][1]['fields'] = (
                'street', 'house_number', 'town', 'county', 'country', 
                'property_rating', 'room_capacity', 'people_capacity', 
                'owner', 'property_supervisor'
            )
        else:  # When adding a new Property
            fieldsets[0][1]['fields'] = (
                'street', 'house_number', 'town', 'county', 'country', 
                'property_rating', 'room_capacity', 'people_capacity', 
                'owner', 'property_supervisor'
            )
        return fieldsets

    inlines = [PropertyTenantHistoryInline]  # Add tenant history as an inline section

    def current_tenants_display(self, obj):
        """Display current tenants in the admin list view."""
        current_tenants = obj.tenant_history.filter(end_date__isnull=True)
        tenants_list = ", ".join([tenant.tenant.username for tenant in current_tenants])
        return format_html(f"<strong>{tenants_list}</strong>") if tenants_list else "No current tenants"

    current_tenants_display.short_description = "Current Tenants"

    def save_model(self, request, obj, form, change):
        """Ensure the number of current tenants does not exceed capacity."""
        super().save_model(request, obj, form, change)
        current_tenants_count = obj.tenant_history.filter(end_date__isnull=True).count()
        if current_tenants_count > obj.people_capacity:
            raise ValueError(
                f"The number of current tenants ({current_tenants_count}) exceeds the property's capacity ({obj.people_capacity})."
            )

# Register Property with the admin interface
admin.site.register(Property, PropertyAdmin)
