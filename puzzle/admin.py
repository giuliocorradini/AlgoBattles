from django.contrib import admin

from .models import Puzzle, Category, PuzzleTest, Attempt

admin.site.register(Puzzle)
admin.site.register(Category)
admin.site.register(PuzzleTest)
admin.site.register(Attempt)