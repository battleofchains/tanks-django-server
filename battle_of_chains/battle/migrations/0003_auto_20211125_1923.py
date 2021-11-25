# Generated by Django 3.2.9 on 2021-11-25 16:23

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0002_alter_battle_status'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectile',
            name='max_damage',
        ),
        migrations.RemoveField(
            model_name='projectile',
            name='min_damage',
        ),
        migrations.RemoveField(
            model_name='projectiletype',
            name='max_damage_default',
        ),
        migrations.RemoveField(
            model_name='projectiletype',
            name='min_damage_default',
        ),
        migrations.AddField(
            model_name='projectile',
            name='avg_damage',
            field=models.PositiveIntegerField(default=10),
        ),
        migrations.AddField(
            model_name='projectile',
            name='ricochet_chance',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='Ricochet chance, %'),
        ),
        migrations.AddField(
            model_name='projectiletype',
            name='avg_damage_default',
            field=models.PositiveIntegerField(default=10),
        ),
        migrations.AddField(
            model_name='projectiletype',
            name='ricochet_chance_default',
            field=models.PositiveSmallIntegerField(default=1, validators=[django.core.validators.MaxValueValidator(100)], verbose_name='Ricochet chance default, %'),
        ),
    ]
