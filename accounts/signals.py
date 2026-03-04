from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver

from accounts.middleware import invalidate_domain_cache


@receiver([post_save, post_delete], sender='accounts.Teacher')
def clear_cors_cache(sender, **kwargs):
    invalidate_domain_cache()
