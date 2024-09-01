# Code Contests dataset import

from django.db import migrations
from datasets import load_dataset
import sys

isTesting = ("test" in sys.argv)

def load_train_dataset():
    ds = load_dataset("deepmind/code_contests")
    train_ds = ds["train"]

    return train_ds

def get_difficulty_for(item):
    diff = item.get("difficulty")

    match diff:
        case 0 | 1 | 5: # Unknown, easy or external
            return "E"
        case 2:
            return "M"
        case 3 | 4:
            return "H"
        
    if diff >= 7 and diff <= 8:
        return "E"
    elif diff >= 9 and diff <= 15:
        return "M"
    else:
        return "H"

def import_into_db(apps, schema_editor):
    ds = load_train_dataset()

    Puzzle = apps.get_model("puzzle", "Puzzle")
    PuzzleTest = apps.get_model("puzzle", "PuzzleTest")
    Category = apps.get_model("puzzle", "Category")

    for item in ds:
        categories = [
            c for c, _ in map(lambda tag: Category.objects.get_or_create(name=tag), item.get("cf_tags"))
        ]

        private_tests = item.get("private_tests")
        public_tests = item.get("public_tests")

        if not private_tests and not public_tests:
            continue

        if not private_tests:
            private_tests = public_tests
            public_tests = {}

        time_limit = item.get("time_limit")
        time_limit = time_limit.get("seconds") * 1000 + time_limit.get("nanos") if time_limit else 0

        p = Puzzle.objects.create(
            title=item.get("name"),
            difficulty=get_difficulty_for(item),
            description=item.get("description"),
            time_constraint=time_limit,
            memory_constraint=item.get("memory_limit_bytes", 0),
        )

        p.categories.set(categories)
        p.save()

        print(p)

        for provided_input, expected_output in zip(private_tests.get("input", []), private_tests.get("output"), []):
            t = PuzzleTest.objects.create(
                input=provided_input,
                output=expected_output,
                is_private=True,
                puzzle=p
            )

        for provided_input, expected_output in zip(private_tests.get("input", []), private_tests.get("output"), []):
            t = PuzzleTest.objects.create(
                input=provided_input,
                output=expected_output,
                is_private=False,
                puzzle=p
            )


def remove_from_db(apps, schema_editor):
    ds = load_train_dataset()

    Puzzle = apps.get_model("puzzle", "Puzzle")

    for item in ds:
        title = item.get("name")
        Puzzle.objects.filter(title=title).delete()


class Migration(migrations.Migration):

    dependencies = [
        ('puzzle', '0014_puzzle_visibility'),
    ]

    operations = [
        migrations.RunPython(
            code=import_into_db,
            reverse_code=remove_from_db
        )
    ] if not isTesting else []
