# Generated by Django 5.1.1 on 2024-09-03 20:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('userprofile', '0003_alter_profile_picture'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='picture',
            field=models.ImageField(upload_to='propics'),
        ),
    ]
