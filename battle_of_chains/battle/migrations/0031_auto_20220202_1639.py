# Generated by Django 3.2.9 on 2022-02-02 13:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0030_auto_20220202_1225'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='projectile',
            name='critical_hit_bonus',
        ),
        migrations.RemoveField(
            model_name='projectiletype',
            name='critical_hit_bonus_default',
        ),
        migrations.AddField(
            model_name='projectile',
            name='penetration',
            field=models.PositiveSmallIntegerField(default=50),
        ),
        migrations.AddField(
            model_name='projectiletype',
            name='penetration_default',
            field=models.PositiveSmallIntegerField(default=50),
        ),
        migrations.AlterField(
            model_name='tank',
            name='armor',
            field=models.PositiveIntegerField(default=100),
        ),
        migrations.AlterField(
            model_name='tanktype',
            name='armor_default',
            field=models.PositiveSmallIntegerField(default=100),
        ),
    ]
