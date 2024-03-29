# Generated by Django 3.2.9 on 2022-01-17 15:05

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('battle', '0019_tank_hull_sprite'),
    ]

    operations = [
        migrations.CreateModel(
            name='Offer',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=100)),
                ('amount', models.PositiveIntegerField()),
                ('price', models.DecimalField(decimal_places=6, default=0, max_digits=15)),
                ('is_active', models.BooleanField(default=True)),
                ('base_tank', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='offers', to='battle.tank')),
            ],
        ),
    ]
