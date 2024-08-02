from django.db import models
from django.db.models import constraints
from django.utils.translation import gettext_lazy as _
from allauth.account.models import get_user_model

class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)


class Puzzle(models.Model):
    title = models.CharField(max_length=150)

    class DifficultyLevel(models.TextChoices):
        EASY = "E", _("Easy")
        MEDIUM = "M", _("Medium")
        HARD = "H", _("Hard")

    difficulty = models.CharField(
        max_length=1,
        choices=DifficultyLevel,
        default=DifficultyLevel.EASY
    )

    description = models.TextField()

    time_constraint = models.IntegerField() # in us
    memory_constraint = models.IntegerField()

    categories = models.ManyToManyField(Category)


class PuzzleTest(models.Model):
    input = models.TextField()
    output = models.TextField()
    
    is_private = models.BooleanField()

    problem = models.ForeignKey(Puzzle, on_delete=models.CASCADE)


class Development(models.Model):
    """Each user develops (once) on a puzzle, that holds every attempt at solving it"""

    puzzle = models.ForeignKey(Puzzle, on_delete=models.CASCADE)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    constraints = [
        constraints.UniqueConstraint(puzzle, user, name="unique_puzzle_development_per_user")
    ]

class Attempt(models.Model):
    """An attempt of solving the puzzle. Triggers a build and a test in the solver facility"""

    development = models.ForeignKey(Development, on_delete=models.CASCADE)
    passed = models.BooleanField()
    results = models.TextField()    # Test results JSON-encoded

