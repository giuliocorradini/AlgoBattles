# Publishers are companies, or institutions, that are accredited by the webmaster, and can publish new puzzles
# or edit existing ones.
# This migration introduces the "editor" group

from django.db import migrations
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models
from django.contrib.auth.models import Group


def add_publisher_group(apps, schema_editor):
    Group.objects.create(name="Publishers")

def reverse_publisher_group(apps, schema_editor):
    Group.objects.remove(name="Publishers")


class Migration(migrations.Migration):

    dependencies = [
        ('puzzle', '0015_code_contests'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.AddField(
            model_name='puzzle',
            name='publisher',
            field=models.ForeignKey(default=None, null=True, on_delete=django.db.models.deletion.SET_DEFAULT, to=settings.AUTH_USER_MODEL),
        ),
        migrations.RunPython(
            code=add_publisher_group,
            reverse_code=reverse_publisher_group
        )
    ]
