# Generated by Django 3.2.9 on 2022-01-13 09:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('battle', '0015_auto_20220113_1256'),
    ]

    operations = [
        migrations.AlterField(
            model_name='country',
            name='image',
            field=models.ImageField(blank=True, null=True, upload_to=''),
        ),
    ]
