# signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.db import models
from .models import CustomUser
from roomie_property.models import Property

@receiver(post_save, sender=CustomUser)
def update_property_on_state_change(sender, instance, created, **kwargs):
    if not created:  # If the Profile is updated (not created)
        # Assuming Property has a field that references the user (owner or supervisor)
        properties = Property.objects.filter(owner=instance.user)  # Update properties where the user is the owner
        for property in properties:
           
            property.save()

