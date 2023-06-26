from django.apps import AppConfig


class StoreConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'store'

    # In order to execute the signals; this method is called when the app is ready
    def ready(self) -> None:
        import store.signals.handlers