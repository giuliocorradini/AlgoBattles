# Generated by Django 5.1 on 2024-09-03 14:51

import django.db.models.functions.text
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzle', '0016_puzzle_publisher'),
    ]

    operations = [
        migrations.AlterField(
            model_name='category',
            name='name',
            field=models.CharField(max_length=100),
        ),
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(django.db.models.functions.text.Lower('name'), name='unique_lower'),
        ),
    ]
