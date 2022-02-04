# Generated by Django 3.2.9 on 2022-02-04 14:31

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0011_auto_20220201_1805'),
        ('battle', '0033_tank_description'),
    ]

    operations = [
        migrations.AddField(
            model_name='battlesettings',
            name='active_network',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='blockchain.network'),
        ),
    ]
