# Generated by Django 4.1 on 2022-08-04 17:24

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('mainApi', '0004_alter_veiculo_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='veiculo',
            name='created',
            field=models.DateTimeField(blank=True, default=datetime.datetime(2022, 8, 4, 17, 24, 5, 867583)),
        ),
        migrations.AlterField(
            model_name='veiculo',
            name='vendido',
            field=models.BooleanField(default=False),
        ),
    ]