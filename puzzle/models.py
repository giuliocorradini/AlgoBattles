from django.db import models
from django.db.models import constraints
from django.contrib.auth.models import User
from django.utils.translation import gettext_lazy as _
from multiplayer.models import Challenge
from django.contrib.postgres.indexes import GinIndex
from django.contrib.postgres.search import SearchVectorField, SearchVector

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    featured = models.BooleanField(default=False)


class Puzzle(models.Model):
    title = models.CharField(max_length=150)

    class DifficultyLevel(models.TextChoices):
        EASY = "E", _("Easy")
        MEDIUM = "M", _("Medium")
        HARD = "H", _("Hard")

    difficulty = models.CharField(
        max_length=1,
        choices=DifficultyLevel.choices,
        default=DifficultyLevel.EASY
    )

    description = models.TextField()

    time_constraint = models.IntegerField() # in us
    memory_constraint = models.IntegerField()

    categories = models.ManyToManyField(Category)

    search_vector = models.GeneratedField(
        db_persist=True,
        expression=SearchVector(
            "title", "description", config="english"
        ),
        output_field=SearchVectorField(),
    )
    class Meta:
        indexes = [GinIndex(fields=['search_vector'])]

    class Visibility(models.TextChoices):
        PUBLIC = "P", _("Public")
        HIDDEN = "H", _("Hidden")
        PRIVATE = "R", _("Private")

    visibility = models.CharField(
        max_length=1,
        choices=Visibility.choices,
        default=Visibility.PUBLIC
    )

    publisher = models.ForeignKey(User, on_delete=models.SET_DEFAULT, null=True, default=None)


class PuzzleTest(models.Model):
    input = models.TextField()
    output = models.TextField()
    
    is_private = models.BooleanField()

    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)


class Development(models.Model):
    """Each user develops (once) on a puzzle, that holds every attempt at solving it"""

    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    constraints = [
        constraints.UniqueConstraint(puzzle, user, name="unique_puzzle_development_per_user")
    ]

    completed = models.BooleanField(default=False)

    challenge = models.ForeignKey(Challenge, on_delete=models.CASCADE, default=None, null=True)

class Attempt(models.Model):
    """An attempt of solving the puzzle. Triggers a build and a test in the solver facility"""

    development = models.ForeignKey(Development, on_delete=models.CASCADE)
    passed = models.BooleanField(default=False)
    build_error = models.BooleanField(default=False)
    results = models.TextField()    # Test results JSON-encoded
    on_date = models.DateTimeField(auto_now=True)
    task_id = models.CharField(max_length=255)

