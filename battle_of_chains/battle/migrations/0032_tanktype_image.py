# Generated by Django 3.2.9 on 2022-02-03 13:35

import battle_of_chains.battle.models
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0031_auto_20220202_1639'),
    ]

    operations = [
        migrations.AddField(
            model_name='tanktype',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=battle_of_chains.battle.models.upload_tank_type_path),
        ),
    ]
