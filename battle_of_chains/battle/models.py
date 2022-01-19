from colorful.fields import RGBColorField
from django.core.validators import MaxValueValidator
from django.db import models


def upload_maps_path(instance, filename):
    return f'maps/{instance.pk}/{filename}'


def upload_tank_path(instance, filename):
    return f'tanks/{instance.pk}/{filename}'


class Map(models.Model):
    name = models.CharField(unique=True, max_length=255)
    json_file = models.FileField(verbose_name='JSON spec', upload_to=upload_maps_path)
    sprite_file = models.FileField(verbose_name='Sprites', upload_to=upload_maps_path)
    is_active = models.BooleanField(default=True)

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


class TankType(models.Model):
    name = models.CharField(max_length=100, unique=True)
    hp_step = models.PositiveSmallIntegerField(default=100)
    max_equipment = models.PositiveSmallIntegerField(default=1)
    moving_price_default = models.PositiveIntegerField(default=1)
    damage_bonus_default = models.PositiveSmallIntegerField(default=1, verbose_name='Damage bonus default, %',
                                                            validators=[MaxValueValidator(100)])
    critical_chance_default = models.PositiveSmallIntegerField(default=1, verbose_name="Critical hit chance default, %",
                                                               validators=[MaxValueValidator(100)])
    overlook_default = models.PositiveSmallIntegerField(default=3, verbose_name='Number of hex view default')
    armor_default = models.PositiveSmallIntegerField(default=50)
    block_chance_default = models.PositiveSmallIntegerField(default=1, verbose_name='Chance to block default, %',
                                                            validators=[MaxValueValidator(100)])

    def __str__(self):
        return self.name


class Tank(models.Model):
    name = models.CharField(max_length=100, blank=True, null=True)
    image = models.ImageField(upload_to=upload_tank_path, null=True, blank=True)
    owner = models.ForeignKey('users.User', on_delete=models.SET_NULL, related_name='tanks', null=True, blank=True)
    hp = models.PositiveIntegerField(default=100)
    moving_price = models.PositiveIntegerField(default=1)
    damage_bonus = models.PositiveSmallIntegerField(default=1, verbose_name='Damage bonus, %',
                                                    validators=[MaxValueValidator(100)])
    critical_chance = models.PositiveSmallIntegerField(default=1, verbose_name="Critical hit chance, %",
                                                       validators=[MaxValueValidator(100)])
    overlook = models.PositiveSmallIntegerField(default=3, verbose_name='Number of hex view')
    armor = models.PositiveIntegerField(default=50)
    block_chance = models.PositiveSmallIntegerField(default=1, verbose_name='Chance to block, %',
                                                    validators=[MaxValueValidator(100)])
    level = models.PositiveIntegerField(default=1, validators=[MaxValueValidator(15)])
    type = models.ForeignKey(TankType, on_delete=models.PROTECT, related_name='tanks')
    for_sale = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=15, decimal_places=6, default=0)
    sprite = models.ImageField(upload_to=upload_tank_path, null=True, blank=True)
    hull_sprite = models.ImageField(upload_to=upload_tank_path, null=True, blank=True)
    basic_free_tank = models.BooleanField(default=False)
    country = models.ForeignKey('Country', on_delete=models.SET_NULL, null=True, blank=True)
    origin_offer = models.ForeignKey('market.Offer', on_delete=models.SET_NULL, null=True, blank=True)

    def __str__(self):
        return f"{self.owner or None} | {self.name}" if self.name \
            else f'{self.owner or None} | {self.type.name} {self.pk}'

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
    fire_price_default = models.PositiveIntegerField(default=1)

    def __str__(self):
        return self.name


class Projectile(models.Model):
    type = models.ForeignKey(ProjectileType, on_delete=models.PROTECT, related_name='projectiles')
    avg_damage = models.PositiveIntegerField(default=10)
    distance = models.PositiveSmallIntegerField(default=5)
    environment_damage = models.PositiveIntegerField(default=15)
    critical_hit_bonus = models.PositiveSmallIntegerField(default=1, verbose_name='Critical hit bonus, %',
                                                          validators=[MaxValueValidator(100)])
    ammo = models.PositiveIntegerField(default=10)
    radius = models.PositiveSmallIntegerField(default=0)
    ricochet_chance = models.PositiveSmallIntegerField(default=1,
                                                       verbose_name='Ricochet chance, %',
                                                       validators=[MaxValueValidator(100)])
    tank = models.ForeignKey('Tank', on_delete=models.CASCADE, related_name='projectiles', null=True, blank=True)
    fire_price = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f'{self.type.name} {self.pk}'


class Country(models.Model):
    name = models.CharField(max_length=100)
    image = models.ImageField(blank=True, null=True)

    class Meta:
        verbose_name_plural = 'Countries'

    def __str__(self):
        return self.name
