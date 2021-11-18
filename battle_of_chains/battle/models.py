from colorful.fields import RGBColorField
from django.db import models


def upload_maps_path(instance, filename):
    return f'maps/{instance.name}/{filename}'


class Map(models.Model):
    name = models.CharField(unique=True, max_length=255)
    json_file = models.FileField(verbose_name='JSON spec', upload_to=upload_maps_path)
    sprite_file = models.FileField(verbose_name='Sprites', upload_to=upload_maps_path)

    def __str__(self):
        return self.name


class Battle(models.Model):

    class STATUS:
        WAITING = 'waiting'
        RUNNING = 'running'
        FINISHED = 'finished'
        CHOICES = (
            (WAITING, WAITING),
            (RUNNING, RUNNING),
            (FINISHED, FINISHED),
        )

    map = models.ForeignKey(Map, on_delete=models.PROTECT, related_name='battles')
    created = models.DateTimeField(auto_now_add=True)
    duration = models.PositiveIntegerField(default=0, verbose_name='Duration, seconds')
    status = models.CharField(choices=STATUS.CHOICES, max_length=10)
    players = models.ManyToManyField('users.User', related_name='battles')
    winner = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f'Battle {self.pk}'


class Squad(models.Model):
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='squads')
    name = models.CharField(max_length=255, default='My super squad')

    def __str__(self):
        return self.name


class TankType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    hp_step = models.PositiveSmallIntegerField(default=100)
    max_weapons = models.PositiveSmallIntegerField(default=1)
    max_equipment = models.PositiveSmallIntegerField(default=1)
    action_points_default = models.PositiveIntegerField(default=100)
    moving_points_default = models.PositiveIntegerField(default=100)
    damage_bonus_default = models.PositiveSmallIntegerField(default=1, verbose_name='Damage bonus default, %')
    critical_chance_default = models.PositiveSmallIntegerField(default=1, verbose_name="Critical hit chance default, %")
    overlook_default = models.PositiveSmallIntegerField(default=3, verbose_name='Number of hex view default')
    armor_default = models.PositiveSmallIntegerField(default=50)
    block_chance_default = models.PositiveSmallIntegerField(default=1, verbose_name='Chance to block default, %')
    fuel_default = models.PositiveIntegerField(default=100)

    def __str__(self):
        return self.name


class Tank(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='tanks')
    squad = models.ForeignKey(Squad, on_delete=models.SET_NULL, blank=True, null=True, related_name='tanks')
    hp = models.PositiveIntegerField(default=100)
    action_points = models.PositiveIntegerField(default=100)
    moving_points = models.PositiveIntegerField(default=100)
    damage_bonus = models.PositiveSmallIntegerField(default=1, verbose_name='Damage bonus, %')
    critical_chance = models.PositiveSmallIntegerField(default=1, verbose_name="Critical hit chance, %")
    overlook = models.PositiveSmallIntegerField(default=3, verbose_name='Number of hex view')
    armor = models.PositiveIntegerField(default=50)
    block_chance = models.PositiveSmallIntegerField(default=1, verbose_name='Chance to block, %')
    fuel = models.PositiveIntegerField(default=100)
    level = models.PositiveIntegerField(default=1)
    type = models.ForeignKey(TankType, on_delete=models.PROTECT, related_name='tanks')

    def __str__(self):
        return self.name if self.name else f'{self.type.name} {self.pk}'

    @property
    def max_hp(self):
        return self.level * self.type.hp_step


class WeaponType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = RGBColorField(verbose_name='Color')
    tank_types = models.ManyToManyField(TankType, related_name='weapon_types')
    max_damage_default = models.PositiveIntegerField(default=20)
    min_damage_default = models.PositiveIntegerField(default=10)
    distance_default = models.PositiveSmallIntegerField(default=5)
    environment_damage_default = models.PositiveIntegerField(default=15)
    critical_hit_bonus_default = models.PositiveSmallIntegerField(default=1,
                                                                  verbose_name='Critical hit bonus default, %')
    usage_limit_default = models.PositiveSmallIntegerField(default=1)

    def __str__(self):
        return self.name


class Weapon(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='weapons')
    max_damage = models.PositiveIntegerField(default=20)
    min_damage = models.PositiveIntegerField(default=10)
    distance = models.PositiveSmallIntegerField(default=5)
    environment_damage = models.PositiveIntegerField(default=15)
    critical_hit_bonus = models.PositiveSmallIntegerField(default=1, verbose_name='Critical hit bonus, %')
    usage_limit = models.PositiveSmallIntegerField(default=1)
    type = models.ForeignKey(WeaponType, on_delete=models.PROTECT, related_name='weapons')
    ammo = models.PositiveIntegerField(default=10)
    tank = models.ForeignKey('Tank', on_delete=models.SET_NULL, related_name='weapons', null=True, blank=True)

    def __str__(self):
        return self.name if self.name else f'{self.type.name} {self.pk}'
