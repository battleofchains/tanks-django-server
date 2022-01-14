# Generated by Django 3.2.9 on 2021-12-30 15:13

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('blockchain', '0006_auto_20211230_1638'),
        ('users', '0003_auto_20211122_1505'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='wallet',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='user', to='blockchain.wallet'),
        ),
    ]