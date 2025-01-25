from django.contrib import admin
from .models import Property

class PropertyAdmin(admin.ModelAdmin):
    list_display = ('street', 'house_number', 'town', 'county', 'country', 'property_rating', 'room_capacity', 'people_capacity', 'owner', 'property_supervisor')
    search_fields = ('street', 'town', 'county', 'country', 'owner__username', 'property_supervisor__username')

    def get_fieldsets(self, request, obj=None):
        fieldsets = super().get_fieldsets(request, obj)
        if obj:  # If editing an existing Property
            fieldsets[0][1]['fields'] = (
                'street', 'house_number', 'town', 'county', 'country', 'property_rating', 'room_capacity', 'people_capacity', 'owner', 'property_supervisor'
            )
        else:  # When adding a new Property
            fieldsets[0][1]['fields'] = ('street', 'house_number', 'town', 'county', 'country', 'property_rating', 'room_capacity', 'people_capacity', 'owner', 'property_supervisor')
        return fieldsets

# Register Property with the admin interface
admin.site.register(Property, PropertyAdmin)
