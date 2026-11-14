from django.apps import AppConfig
from django.db.models.signals import post_migrate


class ApiConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "api"

    def ready(self):
        post_migrate.connect(self._seed_after_migrate, sender=self)

    @staticmethod
    def _seed_after_migrate(sender, **kwargs):
        from .seed import seed_all

        seed_all()
