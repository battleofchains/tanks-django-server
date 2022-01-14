from django.db.models.signals import post_save
from django.dispatch import receiver

from battle_of_chains.utils.functions import generate_first_squad

from .models import User


@receiver(post_save, sender=User)
def create_first_squad(sender, instance, created, **kwargs):
    if created:
        generate_first_squad(instance)
