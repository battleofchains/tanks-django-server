# Generated by Django 3.2.9 on 2022-02-07 13:48

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0034_battlesettings_active_network'),
    ]

    operations = [
        migrations.AlterField(
            model_name='battle',
            name='map',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='battles', to='battle.map'),
        ),
    ]
