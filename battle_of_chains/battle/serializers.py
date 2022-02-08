from datetime import timedelta

from django.conf import settings
from django.utils import timezone
from rest_framework import serializers
from rest_framework.exceptions import APIException
from rest_framework.status import HTTP_409_CONFLICT

from battle_of_chains.utils.functions import create_tank_from_offer

from .models import BattleSettings, BattleType, Country, Map, Projectile, ProjectileType, Tank, TankType


class TankTokenException(APIException):
    status_code = HTTP_409_CONFLICT
    default_code = 'token_exists'
    default_detail = 'NFT token for this tank already exists'


class MapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Map
        fields = '__all__'


class BattleTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = BattleType
        fields = '__all__'


class TankTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = TankType
        fields = ('id', 'name', 'image')


class CountrySerializer(serializers.ModelSerializer):
    class Meta:
        model = Country
        fields = '__all__'


class TankSerializer(serializers.ModelSerializer):
    type = TankTypeSerializer()
    country = CountrySerializer()

    class Meta:
        model = Tank
        fields = '__all__'
        read_only_fields = ['owner']


class ProjectileTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProjectileType
        fields = '__all__'


class ProjectileSerializer(serializers.ModelSerializer):
    type = serializers.StringRelatedField()

    class Meta:
        model = Projectile
        fields = '__all__'


class TankNftMetaSerializer(serializers.ModelSerializer):
    symbol = serializers.SerializerMethodField()
    description = serializers.SerializerMethodField()
    external_url = serializers.SerializerMethodField()
    attributes = serializers.SerializerMethodField()

    class Meta:
        model = Tank
        fields = (
            'name',
            'symbol',
            'description',
            'image',
            'external_url',
            'attributes',
        )

    def get_symbol(self, obj):
        return BattleSettings.get_solo().nft_ticker

    def get_description(self, obj):
        return 'Battle of Chains tank NFT'

    def get_external_url(self, obj):
        return settings.SITE_URL

    def get_attributes(self, obj):
        attributes = []
        for attr in (
            'level', 'hp', 'armor', 'moving_price', 'critical_chance', 'overlook', 'rebound_chance'
        ):
            value = getattr(obj, attr)
            attributes.append({'trait_type': attr, 'value': value})
        return attributes


class TankNewTokenIdSerializer(serializers.ModelSerializer):
    token_id = serializers.SerializerMethodField()

    class Meta:
        model = Tank
        fields = ('name', 'token_id')

    def get_token_id(self, obj):
        if obj.basic_free_tank:
            if hasattr(obj, 'offer'):
                if obj.offer.amount_sold >= obj.offer.amount:
                    raise TankTokenException(detail='This offer is sold out', code='sold_out')
                existing = Tank.objects.filter(
                    origin_offer=obj.offer,
                    owner__isnull=True,
                    nft__isnull=True,
                    date_add__lt=timezone.now() - timedelta(seconds=60*15)
                ).first()
                if existing:
                    return existing.id
                new_tank = create_tank_from_offer(obj.offer)
                return new_tank.id
            else:
                raise TankTokenException(detail='This tank has no offer', code='no_offer')
        elif not hasattr(obj, 'nft'):
            return obj.id
        else:
            raise TankTokenException()


class GlobalSettingsSerializer(serializers.ModelSerializer):
    class Meta:
        model = BattleSettings
        fields = '__all__'
