# Generated by Django 3.2.9 on 2022-01-25 15:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0023_auto_20220121_1956'),
    ]

    operations = [
        migrations.AddField(
            model_name='tank',
            name='date_mod',
            field=models.DateTimeField(auto_now=True, verbose_name='Modified'),
        ),
    ]
