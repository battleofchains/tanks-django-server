from colorful.fields import RGBColorField
from django.core.validators import MaxValueValidator
from django.db import models


def upload_maps_path(instance, filename):
    return f'maps/{instance.name}/{filename}'


def upload_tank_path(instance, filename):
    return f'tanks/{instance.pk}/{filename}'


class Map(models.Model):
    name = models.CharField(unique=True, max_length=255)
    json_file = models.FileField(verbose_name='JSON spec', upload_to=upload_maps_path)
    sprite_file = models.FileField(verbose_name='Sprites', upload_to=upload_maps_path)

    def __str__(self):
        return self.name


class BattleType(models.Model):
    name = models.CharField(max_length=30, primary_key=True)
    players_number = models.PositiveSmallIntegerField()
    player_tanks_number = models.PositiveSmallIntegerField(default=3)

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
    status = models.CharField(choices=STATUS.CHOICES, max_length=10, default=STATUS.WAITING)
    players = models.ManyToManyField('users.User', related_name='battles')
    winner = models.ForeignKey('users.User', on_delete=models.SET_NULL, null=True, blank=True)
    type = models.ForeignKey(BattleType, on_delete=models.CASCADE, related_name='battles')

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
    max_equipment = models.PositiveSmallIntegerField(default=1)
    action_points_default = models.PositiveIntegerField(default=100)
    moving_points_default = models.PositiveIntegerField(default=100)
    damage_bonus_default = models.PositiveSmallIntegerField(default=1, verbose_name='Damage bonus default, %',
                                                            validators=[MaxValueValidator(100)])
    critical_chance_default = models.PositiveSmallIntegerField(default=1, verbose_name="Critical hit chance default, %",
                                                               validators=[MaxValueValidator(100)])
    overlook_default = models.PositiveSmallIntegerField(default=3, verbose_name='Number of hex view default')
    armor_default = models.PositiveSmallIntegerField(default=50)
    block_chance_default = models.PositiveSmallIntegerField(default=1, verbose_name='Chance to block default, %',
                                                            validators=[MaxValueValidator(100)])
    fuel_default = models.PositiveIntegerField(default=100)

    def __str__(self):
        return self.name


class Tank(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to=upload_tank_path, null=True, blank=True)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='tanks')
    squad = models.ForeignKey(Squad, on_delete=models.SET_NULL, blank=True, null=True, related_name='tanks')
    hp = models.PositiveIntegerField(default=100)
    action_points = models.PositiveIntegerField(default=100)
    moving_points = models.PositiveIntegerField(default=100)
    damage_bonus = models.PositiveSmallIntegerField(default=1, verbose_name='Damage bonus, %',
                                                    validators=[MaxValueValidator(100)])
    critical_chance = models.PositiveSmallIntegerField(default=1, verbose_name="Critical hit chance, %",
                                                       validators=[MaxValueValidator(100)])
    overlook = models.PositiveSmallIntegerField(default=3, verbose_name='Number of hex view')
    armor = models.PositiveIntegerField(default=50)
    block_chance = models.PositiveSmallIntegerField(default=1, verbose_name='Chance to block, %',
                                                    validators=[MaxValueValidator(100)])
    fuel = models.PositiveIntegerField(default=100)
    level = models.PositiveIntegerField(default=1)
    type = models.ForeignKey(TankType, on_delete=models.PROTECT, related_name='tanks')

    def __str__(self):
        return self.name if self.name else f'{self.type.name} {self.pk}'

    @property
    def max_hp(self):
        return self.level * self.type.hp_step


class ProjectileType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    color = RGBColorField(verbose_name='Color')
    tank_types = models.ManyToManyField(TankType, related_name='projectile_types')
    avg_damage_default = models.PositiveIntegerField(default=10)
    distance_default = models.PositiveSmallIntegerField(default=5)
    environment_damage_default = models.PositiveIntegerField(default=15)
    critical_hit_bonus_default = models.PositiveSmallIntegerField(default=1,
                                                                  verbose_name='Critical hit bonus default, %',
                                                                  validators=[MaxValueValidator(100)])
    radius_default = models.PositiveSmallIntegerField(default=0)
    ricochet_chance_default = models.PositiveSmallIntegerField(default=1,
                                                               verbose_name='Ricochet chance default, %',
                                                               validators=[MaxValueValidator(100)])

    def __str__(self):
        return self.name


class Projectile(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    owner = models.ForeignKey('users.User', on_delete=models.CASCADE, related_name='projectiles')
    avg_damage = models.PositiveIntegerField(default=10)
    distance = models.PositiveSmallIntegerField(default=5)
    environment_damage = models.PositiveIntegerField(default=15)
    critical_hit_bonus = models.PositiveSmallIntegerField(default=1, verbose_name='Critical hit bonus, %',
                                                          validators=[MaxValueValidator(100)])
    type = models.ForeignKey(ProjectileType, on_delete=models.PROTECT, related_name='projectiles')
    ammo = models.PositiveIntegerField(default=10)
    radius = models.PositiveSmallIntegerField(default=0)
    ricochet_chance = models.PositiveSmallIntegerField(default=1,
                                                       verbose_name='Ricochet chance, %',
                                                       validators=[MaxValueValidator(100)])
    tank = models.ForeignKey('Tank', on_delete=models.CASCADE, related_name='projectiles', null=True, blank=True)

    def __str__(self):
        return self.name if self.name else f'{self.type.name} {self.pk}'
