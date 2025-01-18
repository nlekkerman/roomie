
from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'role', 'roomie_score')  # Display roomie_score in the admin list view
    search_fields = ('user__username', 'role')  # Allow searching by username and role

admin.site.register(Profile, ProfileAdmin)
