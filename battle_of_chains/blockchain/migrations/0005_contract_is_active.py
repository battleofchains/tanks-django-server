# Generated by Django 3.2.9 on 2021-12-30 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0004_contract_contract_definitions'),
    ]

    operations = [
        migrations.AddField(
            model_name='contract',
            name='is_active',
            field=models.BooleanField(default=True),
        ),
    ]
