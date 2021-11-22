# Generated by Django 3.2.9 on 2021-11-22 12:05

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='battle',
            name='status',
            field=models.CharField(choices=[('waiting', 'waiting'), ('running', 'running'), ('finished', 'finished')], default='waiting', max_length=10),
        ),
    ]