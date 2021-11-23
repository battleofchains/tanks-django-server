from django.contrib.auth import get_user_model
from rest_framework import serializers

from battle_of_chains.battle.serializers import SquadSerializer

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    squads = SquadSerializer(many=True)

    class Meta:
        model = User
        fields = ["username", "url", "wallet", "squads"]

        extra_kwargs = {
            "url": {"view_name": "api:user-detail", "lookup_field": "username"}
        }
