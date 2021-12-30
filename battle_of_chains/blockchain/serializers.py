from django.contrib.auth import get_user_model
from rest_framework import serializers

from .models import Contract, Wallet

User = get_user_model()


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = '__all__'


class WalletSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='email', read_only=True)

    class Meta:
        model = Wallet
        fields = '__all__'
