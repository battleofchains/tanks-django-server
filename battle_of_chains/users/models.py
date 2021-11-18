from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.utils.translation import gettext_lazy as _

from battle_of_chains.blockchain.models import Wallet


class User(AbstractUser):
    """Default user for Battle of Chains."""

    #: First and last name do not cover name patterns around the globe
    name = models.CharField(_("Name of User"), blank=True, max_length=255)
    wallet = models.ForeignKey(Wallet, on_delete=models.SET_NULL, blank=True, null=True)

    def get_absolute_url(self):
        """Get url for user's detail view.

        Returns:
            str: URL for user detail.

        """
        return reverse("users:detail", kwargs={"username": self.username})
