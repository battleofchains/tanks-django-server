from rest_framework import serializers

from .models import BattleType, Map, Projectile, ProjectileType, Tank, TankType


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
        fields = '__all__'


class TankSerializer(serializers.ModelSerializer):
    type = serializers.StringRelatedField()

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
        return 'BOFCNFT'

    def get_description(self, obj):
        return 'Battle of Chains tank NFT'

    def get_external_url(self, obj):
        return 'https://battleofchains.com'

    def get_attributes(self, obj):
        attributes = []
        for attr in (
            'level', 'hp', 'armor', 'moving_price', 'damage_bonus', 'critical_chance', 'overlook', 'block_chance'
        ):
            value = getattr(obj, attr)
            attributes.append({'trait_type': attr, 'value': value})
        return attributes
