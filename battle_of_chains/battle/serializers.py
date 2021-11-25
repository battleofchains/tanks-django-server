from rest_framework import serializers

from .models import BattleType, Map, Projectile, ProjectileType, Squad, Tank, TankType


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


class SquadSerializer(serializers.ModelSerializer):
    tanks = TankSerializer(many=True, required=False)

    class Meta:
        model = Squad
        fields = ('id', 'name', 'tanks')
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
        read_only_fields = ['owner']
