# Generated by Django 3.2.9 on 2021-12-09 06:27

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0006_battletype_player_tanks_number'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='tank',
            name='squad',
        ),
        migrations.DeleteModel(
            name='Squad',
        ),
    ]