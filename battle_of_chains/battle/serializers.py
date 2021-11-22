from rest_framework import serializers

from .models import BattleType, Map, Squad, Tank, TankType


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


class SquadSerializer(serializers.ModelSerializer):
    tanks = TankSerializer(many=True)

    class Meta:
        model = Squad
        fields = ('id', 'name', 'tanks')