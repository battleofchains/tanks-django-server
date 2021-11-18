# Generated by Django 3.2.9 on 2021-11-18 15:18

import battle_of_chains.battle.models
import colorful.fields
from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Map',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, unique=True)),
                ('json_file', models.FileField(upload_to=battle_of_chains.battle.models.upload_maps_path, verbose_name='JSON spec')),
                ('sprite_file', models.FileField(upload_to=battle_of_chains.battle.models.upload_maps_path, verbose_name='Sprites')),
            ],
        ),
        migrations.CreateModel(
            name='Squad',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='My super squad', max_length=255)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='squads', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Tank',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('hp', models.PositiveIntegerField(default=100)),
                ('action_points', models.PositiveIntegerField(default=100)),
                ('moving_points', models.PositiveIntegerField(default=100)),
                ('damage_bonus', models.PositiveSmallIntegerField(default=1, verbose_name='Damage bonus, %')),
                ('critical_chance', models.PositiveSmallIntegerField(default=1, verbose_name='Critical hit chance, %')),
                ('overlook', models.PositiveSmallIntegerField(default=3, verbose_name='Number of hex view')),
                ('armor', models.PositiveIntegerField(default=50)),
                ('block_chance', models.PositiveSmallIntegerField(default=1, verbose_name='Chance to block, %')),
                ('fuel', models.PositiveIntegerField(default=100)),
                ('level', models.PositiveIntegerField(default=1)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='tanks', to=settings.AUTH_USER_MODEL)),
                ('squad', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='tanks', to='battle.squad')),
            ],
        ),
        migrations.CreateModel(
            name='TankType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('hp_step', models.PositiveSmallIntegerField(default=100)),
                ('max_weapons', models.PositiveSmallIntegerField(default=1)),
                ('max_equipment', models.PositiveSmallIntegerField(default=1)),
                ('action_points_default', models.PositiveIntegerField(default=100)),
                ('moving_points_default', models.PositiveIntegerField(default=100)),
                ('damage_bonus_default', models.PositiveSmallIntegerField(default=1, verbose_name='Damage bonus default, %')),
                ('critical_chance_default', models.PositiveSmallIntegerField(default=1, verbose_name='Critical hit chance default, %')),
                ('overlook_default', models.PositiveSmallIntegerField(default=3, verbose_name='Number of hex view default')),
                ('armor_default', models.PositiveSmallIntegerField(default=50)),
                ('block_chance_default', models.PositiveSmallIntegerField(default=1, verbose_name='Chance to block default, %')),
                ('fuel_default', models.PositiveIntegerField(default=100)),
            ],
        ),
        migrations.CreateModel(
            name='WeaponType',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=100, unique=True)),
                ('color', colorful.fields.RGBColorField(verbose_name='Color')),
                ('tank_types', models.ManyToManyField(related_name='weapon_types', to='battle.TankType')),
            ],
        ),
        migrations.CreateModel(
            name='Weapon',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=100, null=True)),
                ('max_damage', models.PositiveIntegerField(default=20)),
                ('min_damage', models.PositiveIntegerField(default=10)),
                ('distance', models.PositiveSmallIntegerField(default=5)),
                ('environment_damage', models.PositiveIntegerField(default=15)),
                ('critical_hit_bonus', models.PositiveSmallIntegerField(default=1, verbose_name='Critical hit bonus, %')),
                ('usage_limit', models.PositiveSmallIntegerField(default=1)),
                ('ammo', models.PositiveIntegerField(default=10)),
                ('owner', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='weapons', to=settings.AUTH_USER_MODEL)),
                ('tank', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='weapons', to='battle.tank')),
                ('type', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='weapons', to='battle.weapontype')),
            ],
        ),
        migrations.AddField(
            model_name='tank',
            name='type',
            field=models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='tanks', to='battle.tanktype'),
        ),
        migrations.CreateModel(
            name='Battle',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('duration', models.PositiveIntegerField(default=0, verbose_name='Duration, seconds')),
                ('status', models.CharField(choices=[('waiting', 'waiting'), ('running', 'running'), ('finished', 'finished')], max_length=10)),
                ('map', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='battles', to='battle.map')),
                ('players', models.ManyToManyField(related_name='battles', to=settings.AUTH_USER_MODEL)),
                ('winner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
