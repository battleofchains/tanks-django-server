from django.contrib.auth import get_user_model
from rest_framework import serializers
from web3.auto import w3

from .models import Contract, Wallet, Network

User = get_user_model()


class ContractSerializer(serializers.ModelSerializer):
    class Meta:
        model = Contract
        fields = '__all__'


class WalletSerializer(serializers.ModelSerializer):
    user = serializers.SlugRelatedField(slug_field='email', read_only=True)
    address = serializers.CharField(required=True, validators=[])

    class Meta:
        model = Wallet
        fields = '__all__'

    def validate_address(self, address):
        if not address or not isinstance(address, str) or not w3.isAddress(address):
            raise serializers.ValidationError(f'Incorrect address ({address})')
        return address


class NetworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Network
        fields = '__all__'
