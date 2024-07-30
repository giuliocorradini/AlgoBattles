# Generated by Django 5.0.6 on 2024-07-30 16:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('puzzle', '0002_rename_puzzlecategories_puzzlecategory'),
    ]

    operations = [
        migrations.AddField(
            model_name='puzzle',
            name='categories',
            field=models.ManyToManyField(to='puzzle.category'),
        ),
        migrations.DeleteModel(
            name='PuzzleCategory',
        ),
    ]
