from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
from roomie_user.models import CustomUser

@receiver(post_save, sender=User)
def create_custom_user(sender, instance, created, **kwargs):
    if created:
        CustomUser.objects.create(user=instance)

@receiver(post_save, sender=User)
def save_custom_user(sender, instance, **kwargs):
    instance.custom_user_profile.save()
