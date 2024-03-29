# Generated by Django 3.2.9 on 2021-12-24 17:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0010_auto_20211215_1439'),
    ]

    operations = [
        migrations.AddField(
            model_name='tank',
            name='for_sale',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='tank',
            name='price',
            field=models.DecimalField(decimal_places=6, default=0, max_digits=15),
        ),
    ]
