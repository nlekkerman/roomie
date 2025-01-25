from django.apps import AppConfig

class RoomieUserConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'  # This specifies the type of auto field for primary keys (optional)
    name = 'roomie_user'  # This is the name of your app
    verbose_name = "Roomie User Management"  # Optional: A human-readable name for the app
    label = 'roomie_user'  # Optional: A short, unique label for the app (defaults to the app name)

    def ready(self):
        # Optional: Any initialization code for the app when Django starts up
        import roomie_user.signals  # Example: Import signals if you have custom signals for the app
