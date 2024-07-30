from django.db import models
from django.utils.translation import gettext_lazy as _

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
